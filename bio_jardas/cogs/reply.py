import random
import re

import structlog
from disnake import Message as DiscordMessage
from disnake.ext.commands import Bot, Cog, Context, group
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db.base import transaction, transactional
from bio_jardas.db.repositories.message import MessageRepo
from bio_jardas.decorators import skip_bots_and_commands
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import ChannelAlreadyRegisteredError, MessageService

logger = structlog.stdlib.get_logger()


class ReplyCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ruff: noqa: ARG002
    @Cog.listener("on_message")
    @skip_bots_and_commands
    @transactional
    async def reply(
        self, message: DiscordMessage, *, context: Context[Bot], session: AsyncSession
    ) -> None:
        author = message.author
        channel = message.channel
        config_service = ConfigService(session)
        message_service = MessageService(self.bot, session)

        intensity = await config_service.get_intensity()
        if random.random() > intensity.reply_probability():
            return

        # TODO: add the -mos dynamic message group
        reply = await message_service.get_reply(author.id, channel.id)
        if not reply:
            return

        await message.reply(reply.text)
        await logger.ainfo(
            "Replied to message",
            author_id=author.id,
            channel_id=channel.id,
            message_group_id=reply.group_id,
            message_id=reply.id,
        )

    @group(name="reply", invoke_without_command=True)
    async def reply_group(self, context: Context):
        await context.send("Available subcommands: add_channel, remove_channel")

    # TODO: improve ux flow
    @reply_group.command("add_channel")
    async def add_channel(self, context: Context):
        async with transaction() as session:
            message_service = MessageService(self.bot, session)

            try:
                await message_service.create_default_message_group_choices(
                    context.channel.id
                )
                await logger.ainfo(
                    "Added default replies to channel",
                    author_id=context.author.id,
                    channel_id=context.channel.id,
                )
            except ChannelAlreadyRegisteredError:
                await logger.aerror(
                    "Attempt to add replies to channel that is already registered",
                    author_id=context.author.id,
                    channel_id=context.channel.id,
                )
                await context.reply("This channel was already registered")
                return
        await context.reply("Registered channel with default message groups")

    @reply_group.command("remove_channel")
    async def remove_channel(
        self, context: Context, *, message_group_names: str | None = None
    ):
        names = re.split(r"[\s,]", message_group_names) if message_group_names else None
        async with transaction() as session:
            message_repo = MessageRepo(session)
            deleted_count = await message_repo.delete_message_group_choices(
                context.channel.id, names
            )
            await logger.ainfo(
                "Removed replies from channel",
                author_id=context.author.id,
                channel_id=context.channel.id,
                deleted_count=deleted_count,
            )
        await context.reply(f"Removed {deleted_count} message groups from channel")
