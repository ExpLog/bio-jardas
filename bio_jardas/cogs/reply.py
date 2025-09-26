import random

import structlog
from dishka import FromDishka
from disnake import Member
from disnake import Message as DiscordMessage
from disnake.ext.commands import (
    BucketType,
    Cog,
    CommandError,
    Context,
    check,
    command,
    cooldown,
    group,
)
from structlog.contextvars import bind_contextvars

from bio_jardas import emojis
from bio_jardas.cogs.base import BaseCog
from bio_jardas.command_checks import is_bot_owner
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.decorators import skip_bots_and_commands
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.dtos.message import UpsertMessageGroupChoice
from bio_jardas.observability import (
    bind_error_cause,
    bind_exception_info,
    bind_listener_context_to_logs,
)
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import ChannelHasMessageGroupsError, MessageService
from bio_jardas.shortcuts import author_id, channel_id
from bio_jardas.utils import standard_embed

logger = structlog.stdlib.get_logger()


# TODO: differentiate between internal errors and user errors in logs
# TODO: actually obey the disabled columns
class ReplyCog(BaseCog):
    @Cog.listener("on_message")
    @skip_bots_and_commands
    @cog_inject
    async def reply_listener(
        self,
        message: DiscordMessage,
        *,
        message_service: FromDishka[MessageService],
        config_service: FromDishka[ConfigService],
    ) -> None:
        bind_listener_context_to_logs(await self.get_message_context(message))
        bind_contextvars(
            listener="ReplyCog.reply_listener",
            listener_event="on_message",
        )

        if self.bot.user.mentioned_in(message):
            reply = await message_service.random_reply_from_group("mention")
            await logger.ainfo(
                "Replied to mention",
                message_group_id=reply.group_id,
                message_id=reply.id,
            )
            await message.channel.send(reply.text)
            return

        intensity = await config_service.get_intensity()
        if random.random() > intensity.reply_probability():
            return

        # TODO: add the -mos dynamic message group
        reply = await message_service.random_message(
            author_id(message), channel_id(message)
        )
        if not reply:
            return

        await logger.ainfo(
            "Replied to message",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        # the original bot doesn't actually send a reply, only a message to the same
        # channel, but I'm not refactoring the reply concept to response
        await message.channel.send(reply.text)

    # reply admin commands
    # root
    @group(name="reply", invoke_without_command=True, case_insensitive=True)
    @check(is_bot_owner)
    async def reply(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    # discoverability
    @reply.command(name="groups")
    @check(is_bot_owner)
    @cooldown(1, 60, BucketType.channel)
    @cog_inject
    async def reply_groups(
        self,
        context: Context,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        groups = await message_service.group_repo.get_many()
        message = ", ".join(f"`{mg.name}`" for mg in groups)
        await context.message.reply(message)

    @reply.group(name="show", invoke_without_command=True)
    @check(is_bot_owner)
    async def reply_show(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @reply_show.command(name="channel")
    @check(is_bot_owner)
    @cooldown(1, 10, BucketType.channel)
    @cog_inject
    async def reply_show_channel(
        self,
        context: Context,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        probabilities = await message_service.reply_probabilities(channel_id(context))
        embed = standard_embed("Channel Message Groups")
        for probability in probabilities:
            embed.add_field(probability.group_name, probability.percentages)
        await context.send(embed=embed, reference=context.message)

    @reply_show.command(name="user")
    @check(is_bot_owner)
    @cooldown(1, 10, BucketType.channel)
    @cog_inject
    async def reply_show_user(
        self,
        context: Context,
        member: Member | None = None,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        target = member if member else context.author
        probabilities = await message_service.reply_probabilities(target.id)
        embed = standard_embed("User Message Groups", description=target.name)
        for probability in probabilities:
            embed.add_field(probability.group_name, probability.percentages)
        if not probabilities:
            embed.add_field("no one likes you", "")
        await context.send(embed=embed, reference=context.message)

    # channel assignment commands (current channel)
    @reply.group(name="channel", invoke_without_command=True)
    @check(is_bot_owner)
    async def reply_channel(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @reply_channel.command(name="add", aliases=("assign", "+"))
    @check(is_bot_owner)
    @cog_inject
    async def reply_channel_add(
        self,
        context: Context,
        group_name: str,
        weight: float = 1.0,
        independent_roll_probability: float = 0.0,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        bind_contextvars(message_group=group_name)
        dto = UpsertMessageGroupChoice(
            snowflake_id=channel_id(context),
            group_name=group_name,
            weight=weight,
            independent_roll_probability=independent_roll_probability,
            is_channel=True,
            is_user=False,
            updated_by=author_id(context),
        )
        await message_service.add_or_update_message_group_choice(dto)
        await logger.ainfo("Added message group to channel")
        await context.message.add_reaction(emojis.SUCCESS)

    @reply_channel.command(name="remove", aliases=("rm", "-"))
    @check(is_bot_owner)
    @cog_inject
    async def reply_channel_remove(
        self,
        context: Context,
        *group_names: str,
        message_service: FromDishka[MessageService],
    ) -> None:
        if not _ensure_group_names(context, group_names):
            return
        deleted_count = await message_service.delete_message_group_choices(
            context.channel.id, group_names
        )
        await logger.ainfo(
            "Removed message groups from channel",
            deleted_count=deleted_count,
            message_groups=group_names,
        )
        reaction = emojis.SUCCESS if deleted_count else emojis.NOT_FOUND
        await context.message.add_reaction(reaction)

    @reply_channel.command(name="clear")
    @check(is_bot_owner)
    @cog_inject
    async def reply_channel_clear(
        self,
        context: Context,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        deleted_count = await message_service.delete_message_group_choices(
            channel_id(context)
        )
        await logger.ainfo(
            "Removed message groups from channel",
            deleted_count=deleted_count,
        )
        await context.message.add_reaction(emojis.SUCCESS)

    @reply_channel.command(name="apply-defaults")
    @check(is_bot_owner)
    @cog_inject
    async def reply_channel_apply_defaults(
        self,
        context: Context,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        await message_service.apply_defaults_to_channel(
            channel_id(context), author_id(context)
        )
        await logger.ainfo(
            "Assigned default message groups to channel",
        )
        await context.message.add_reaction(emojis.SUCCESS)

    # user assignments
    @reply.group(name="user", invoke_without_command=True)
    @check(is_bot_owner)
    async def reply_user(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @reply_user.command(name="add", aliases=("assign", "+"))
    @check(is_bot_owner)
    @cog_inject
    async def reply_user_add(
        self,
        context: Context,
        member: Member,
        group_name: str,
        weight: float = 1.0,
        independent_roll_probability: float = 0.0,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        bind_contextvars(
            target_user_id=member.id,
            target_user_name=member.name,
            message_group=group_name,
        )
        dto = UpsertMessageGroupChoice(
            snowflake_id=member.id,
            group_name=group_name,
            weight=weight,
            independent_roll_probability=independent_roll_probability,
            is_channel=False,
            is_user=True,
            updated_by=author_id(context),
        )
        await message_service.add_or_update_message_group_choice(dto)
        await logger.ainfo(
            "Added message group to user",
        )
        await context.message.add_reaction(emojis.SUCCESS)

    @reply_user.command(name="remove", aliases=("rm", "-"))
    @check(is_bot_owner)
    @cog_inject
    async def reply_user_remove(
        self,
        context: Context,
        member: Member,
        *group_names: str,
        message_service: FromDishka[MessageService],
    ) -> None:
        if not _ensure_group_names(context, group_names):
            return
        deleted_count = await message_service.delete_message_group_choices(
            member.id, group_names
        )
        await logger.ainfo(
            "Removed message groups from channel",
            deleted_count=deleted_count,
            message_groups=group_names,
        )
        reaction = emojis.SUCCESS if deleted_count else emojis.NOT_FOUND
        await context.message.add_reaction(reaction)

    @reply_user.command(name="clear")
    @check(is_bot_owner)
    @cog_inject
    async def reply_user_clear(
        self,
        context: Context,
        member: Member,
        *,
        message_service: FromDishka[MessageService],
    ) -> None:
        deleted_count = await message_service.delete_message_group_choices(member.id)
        await logger.ainfo(
            "Removed message groups from user",
            deleted_count=deleted_count,
        )
        await context.message.add_reaction(emojis.SUCCESS)

    # local error handlers
    @reply_channel_add.error
    @reply_user_add.error
    async def reply_obj_add_error(self, context: Context, exception: CommandError):
        if isinstance(exception.__cause__, EntityNotFoundError):
            bind_error_cause(str(exception.__cause__))
        else:
            bind_exception_info(exception)
        await logger.aerror("Failed to add message group to target")
        await context.message.add_reaction(emojis.FAILURE)

    @reply_channel_apply_defaults.error
    async def reply_channel_apply_defaults_error(
        self, context: Context, exception: CommandError
    ):
        if isinstance(exception.__cause__, ChannelHasMessageGroupsError):
            bind_error_cause(str(exception.__cause__))
        else:
            bind_exception_info(exception)
        await logger.aerror("Failed to apply default message groups to channel")
        await context.message.add_reaction(emojis.FAILURE)


class VocabularyCog(BaseCog):
    @command(name="vocabulary")
    @cog_inject
    async def add_vocabulary(
        self,
        context: Context,
        *,
        text: str,
        message_service: FromDishka[MessageService],
    ):
        reply = await message_service.add_vocabulary(
            text, "user_added_vocabulary", author_id(context)
        )
        await logger.ainfo(
            "Replied to added vocabulary",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(reply.text)

    @command(name="vocabulary_admin")
    @check(is_bot_owner)
    @cog_inject
    async def add_admin_vocabulary(
        self,
        context: Context,
        message_group_name: str,
        *,
        text: str,
        message_service: FromDishka[MessageService],
    ):
        reply = await message_service.add_vocabulary(
            text, message_group_name, author_id(context)
        )
        await logger.ainfo(
            "Replied to added vocabulary",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(reply.text)


async def _ensure_group_names(context: Context, group_names: tuple[str, ...]) -> bool:
    if not group_names:
        await context.reply("No group names given")
        await logger.aerror("No message group names given")
        return False
    return True
