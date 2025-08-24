import random

import structlog
from disnake import Message as DiscordMessage
from disnake.ext.commands import Bot, Cog, Context
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db.base import transactional
from bio_jardas.decorators import skip_bots_and_commands
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import MessageService

logger = structlog.stdlib.get_logger()


class MessageCog(Cog):
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
        choice = await message_service.get_random_message_group_choice(
            author.id, channel.id
        )
        if not choice:
            return
        response = await message_service.get_random_message(choice.group_id)

        await message.reply(response.text)
        await logger.ainfo(
            "Replied to message",
            author_id=author.id,
            channel_id=channel.id,
            message_group_id=response.group_id,
            message_id=response.id,
        )
