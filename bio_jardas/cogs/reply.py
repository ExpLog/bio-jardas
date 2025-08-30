import random

import structlog
from disnake import Member
from disnake import Message as DiscordMessage
from disnake.ext.commands import Bot, Cog, Context, group
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db.base import transaction, transactional
from bio_jardas.db.repositories.message import MessageRepo
from bio_jardas.decorators import skip_bots_and_commands
from bio_jardas.dtos.message import UpsertMessageGroupChoice
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import ChannelAlreadyRegisteredError, MessageService
from bio_jardas.shortcuts import author_id, channel_id, command_qualified_name

logger = structlog.stdlib.get_logger()


class ReplyCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ruff: noqa: ARG002
    @Cog.listener("on_message")
    @skip_bots_and_commands
    @transactional
    async def reply_listener(
        self, message: DiscordMessage, *, context: Context[Bot], session: AsyncSession
    ) -> None:
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

        await message.reply(reply.text)
        await logger.ainfo(
            "Replied to message",
            author_id=author_id(message),
            channel_id=channel_id(message),
            listener="ReplyCog.reply_listener",
            listener_event="on_message",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )

    # reply commands
    # root
    @group(name="reply", invoke_without_command=True, case_insensitive=True)
    async def reply(self, context: Context) -> None:
        # TODO: add some help text
        pass

    # discoverability
    @reply.command(name="groups")
    async def reply_groups(self, context: Context) -> None:
        pass

    @reply.group(name="show", invoke_without_command=True)
    async def reply_show(self, context: Context) -> None:
        # TODO: add some help text
        pass

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
        pass

    @reply_channel.command(name="add", aliases=("assign", "+"))
    async def reply_channel_add(
        self,
        context: Context,
        group_name: str,
        weight: float = 1.0,
        independent_roll_probability: float = 0.0,
    ) -> None:
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
            added = await message_service.add_or_update_message_group_choice(dto)
        await logger.ainfo(
            "Added message group to channel",
            author_id=author_id(context),
            channel_id=channel_id(context),
            command=command_qualified_name(context),
            message_group=group_name,
        )
        await context.message.add_reaction("✅")  # TODO: add opposite reaction on error
        await context.reply(f"Added {len(added)} message groups to channel")

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
            author_id=author_id(context),
            channel_id=channel_id(context),
            command=command_qualified_name(context),
            deleted_count=deleted_count,
            message_groups=group_names,
        )
        await context.reply(f"Removed {deleted_count} message groups from channel")

    @reply_channel.command(name="clear")
    async def reply_channel_clear(self, context: Context) -> None:
        async with transaction() as session:
            message_repo = MessageRepo(session)
            deleted_count = await message_repo.delete_message_group_choices(
                channel_id(context)
            )
        await logger.ainfo(
            "Removed message groups from channel",
            author_id=author_id(context),
            channel_id=channel_id(context),
            command=command_qualified_name(context),
            deleted_count=deleted_count,
        )
        await context.reply("Removed all message groups from channel")

    @reply_channel.command(name="apply-defaults")
    async def reply_channel_apply_defaults(self, context: Context) -> None:
        async with transaction() as session:
            message_service = MessageService(self.bot, session)
            try:
                await message_service.apply_defaults_to_channel(context.channel.id)
            except ChannelAlreadyRegisteredError:
                await logger.aerror(
                    "Attempt to apply default message groups choices to channel with "
                    "choices",
                    author_id=author_id(context),
                    channel_id=channel_id(context),
                    command=command_qualified_name(context),
                )
                await context.reply("This channel already has message groups assigned")
                return
        await logger.ainfo(
            "Applied default message group choices to channel",
            author_id=author_id(context),
            channel_id=channel_id(context),
            command=command_qualified_name(context),
        )
        await context.reply("Applied default message groups to channel")

    # user assignments
    @reply.group(name="user", invoke_without_command=True)
    async def reply_user(self, context: Context) -> None:
        # TODO: add some help text
        pass

    @reply_user.command(name="add", aliases=("assign", "+"))
    async def reply_user_add(
        self, context: Context, member: Member, *groups: str
    ) -> None:
        pass

    @reply_user.command(name="remove", aliases=("rm", "-"))
    async def reply_user_remove(
        self, context: Context, member: Member, *groups: str
    ) -> None:
        pass

    @reply_user.command(name="clear")
    async def reply_user_clear(self, context: Context, member: Member) -> None:
        pass

    # self-service commands (optional)
    @reply.group(name="me", invoke_without_command=True)
    async def reply_me(self, context: Context) -> None:
        # TODO: add some help text
        pass

    @reply_me.command(name="add")
    async def reply_me_add(self, context: Context, *groups: str) -> None:
        pass

    @reply_me.command(name="remove")
    async def reply_me_remove(self, context: Context, *groups: str) -> None:
        pass

    @reply_me.command(name="clear")
    async def reply_me_clear(self, context: Context) -> None:
        pass

    # help fallbacks / local error handlers (optional)
    @reply.error
    async def reply_error(self, context: Context, exc: Exception) -> None:
        pass

    @reply_channel.error
    async def reply_channel_error(self, context: Context, exc: Exception) -> None:
        pass

    @reply_user.error
    async def reply_user_error(self, context: Context, exc: Exception) -> None:
        pass

    @reply_me.error
    async def reply_me_error(self, context: Context, exc: Exception) -> None:
        pass


async def _ensure_group_names(context: Context, group_names: tuple[str, ...]) -> bool:
    if not group_names:
        await context.reply("No group names given")
        await logger.aerror(
            "No message group names given",
            author_id=author_id(context),
            channel_id=channel_id(context),
            command=command_qualified_name(context),
        )
        return False
    return True
