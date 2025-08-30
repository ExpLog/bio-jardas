import random

import structlog
from disnake import Member
from disnake import Message as DiscordMessage
from disnake.ext.commands import Bot, Cog, CommandError, Context, group
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.contextvars import bind_contextvars

from bio_jardas import emojis
from bio_jardas.db.base import transaction, transactional
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.db.repositories.message import MessageRepo
from bio_jardas.decorators import skip_bots_and_commands
from bio_jardas.dtos.message import UpsertMessageGroupChoice
from bio_jardas.observability import (
    bind_error_cause,
    bind_exception_info,
    bind_listener_context_to_logs,
)
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import ChannelHasMessageGroupsError, MessageService
from bio_jardas.shortcuts import author_id, channel_id

logger = structlog.stdlib.get_logger()


# TODO: change success and failure replies to emojis
# TODO: add emojis module
# TODO: add shortcuts success_reaction, error_reaction, uncaught_error_reaction
class ReplyCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_message")
    @skip_bots_and_commands
    @transactional
    async def reply_listener(
        self, message: DiscordMessage, *, context: Context[Bot], session: AsyncSession
    ) -> None:
        bind_listener_context_to_logs(context)
        bind_contextvars(
            listener="ReplyCog.reply_listener",
            listener_event="on_message",
        )

        config_service = ConfigService(session)
        message_service = MessageService(self.bot, session)

        intensity = await config_service.get_intensity()
        if random.random() > intensity.reply_probability():
            return

        # TODO: add the -mos dynamic message group
        reply = await message_service.random_reply(
            author_id(message), channel_id(message)
        )
        if not reply:
            return

        await logger.ainfo(
            "Replied to message",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await message.reply(reply.text)

    # reply commands
    # root
    @group(name="reply", invoke_without_command=True, case_insensitive=True)
    async def reply(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    # discoverability
    @reply.command(name="groups")
    async def reply_groups(self, context: Context) -> None:
        pass

    @reply.group(name="show", invoke_without_command=True)
    async def reply_show(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @reply_show.command(name="channel")
    async def reply_show_channel(self, context: Context) -> None:
        pass

    @reply_show.command(name="user")
    async def reply_show_user(
        self, context: Context, member: Member | None = None
    ) -> None:
        pass

    @reply_show.command(name="defaults")
    async def reply_show_defaults(self, context: Context) -> None:
        pass

    # channel assignment commands (current channel)
    @reply.group(name="channel", invoke_without_command=True)
    async def reply_channel(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @reply_channel.command(name="add", aliases=("assign", "+"))
    async def reply_channel_add(
        self,
        context: Context,
        group_name: str,
        weight: float = 1.0,
        independent_roll_probability: float = 0.0,
    ) -> None:
        bind_contextvars(message_group=group_name)
        dto = UpsertMessageGroupChoice(
            snowflake_id=channel_id(context),
            group_name=group_name,
            weight=weight,
            independent_roll_probability=independent_roll_probability,
            is_channel=True,
            is_user=False,
            last_modified_by=author_id(context),
        )
        async with transaction() as session:
            message_service = MessageService(self.bot, session)
            await message_service.add_or_update_message_group_choice(dto)
        await logger.ainfo("Added message group to channel")
        await context.message.add_reaction(emojis.SUCCESS)

    @reply_channel.command(name="remove", aliases=("rm", "-"))
    async def reply_channel_remove(self, context: Context, *group_names: str) -> None:
        if not _ensure_group_names(context, group_names):
            return
        async with transaction() as session:
            message_repo = MessageRepo(session)
            deleted_count = await message_repo.delete_message_group_choices(
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
    async def reply_channel_clear(self, context: Context) -> None:
        async with transaction() as session:
            message_repo = MessageRepo(session)
            deleted_count = await message_repo.delete_message_group_choices(
                channel_id(context)
            )
        await logger.ainfo(
            "Removed message groups from channel",
            deleted_count=deleted_count,
        )
        await context.message.add_reaction(emojis.SUCCESS)

    @reply_channel.command(name="apply-defaults")
    async def reply_channel_apply_defaults(self, context: Context) -> None:
        async with transaction() as session:
            message_service = MessageService(self.bot, session)
            await message_service.apply_defaults_to_channel(context.channel.id)
        await logger.ainfo(
            "Assigned default message groups to channel",
        )
        await context.message.add_reaction(emojis.SUCCESS)

    # user assignments
    @reply.group(name="user", invoke_without_command=True)
    async def reply_user(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @reply_user.command(name="add", aliases=("assign", "+"))
    async def reply_user_add(
        self,
        context: Context,
        member: Member,
        group_name: str,
        weight: float = 1.0,
        independent_roll_probability: float = 0.0,
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
            last_modified_by=author_id(context),
        )
        async with transaction() as session:
            message_service = MessageService(self.bot, session)
            await message_service.add_or_update_message_group_choice(dto)
        await logger.ainfo(
            "Added message group to user",
        )
        await context.message.add_reaction(emojis.SUCCESS)

    @reply_user.command(name="remove", aliases=("rm", "-"))
    async def reply_user_remove(
        self, context: Context, member: Member, *group_names: str
    ) -> None:
        if not _ensure_group_names(context, group_names):
            return
        async with transaction() as session:
            message_repo = MessageRepo(session)
            deleted_count = await message_repo.delete_message_group_choices(
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
    async def reply_user_clear(self, context: Context, member: Member) -> None:
        async with transaction() as session:
            message_repo = MessageRepo(session)
            deleted_count = await message_repo.delete_message_group_choices(member.id)
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


async def _ensure_group_names(context: Context, group_names: tuple[str, ...]) -> bool:
    if not group_names:
        await context.reply("No group names given")
        await logger.aerror("No message group names given")
        return False
    return True
