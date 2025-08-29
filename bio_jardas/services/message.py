import random

import structlog
from disnake.ext.commands import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db import Message, MessageGroupChoice
from bio_jardas.db.repositories.message import MessageRepo

logger = structlog.stdlib.get_logger()

DEFAULT_CHANNEL_MESSAGE_GROUPS = {
    "dark_joke": 1.0,
    "shower_thought": 1.0,
    "catcall": 2.0,
    "user_added_vocabulary": 5.0,
    "generic_seldom": 2.0,
    "generic_sometimes": 6.0,
    "generic_often": 8.0,
}


class MessageService:
    def __init__(self, bot: Bot, session: AsyncSession):
        self.bot = bot
        self.repo = MessageRepo(session)
        self.session = session

    async def get_random_message_group_choice(
        self, user_id: int, channel_id: int
    ) -> MessageGroupChoice | None:
        choices = await self.repo.get_message_group_choices(user_id, channel_id)
        if not choices:
            return None

        # TODO: add independent roll check here
        return random.choices(choices, [c.weight for c in choices])[0]

    async def get_reply(self, user_id: int, channel_id: int) -> Message | None:
        message_group_choice = await self.get_random_message_group_choice(
            user_id, channel_id
        )
        if not message_group_choice:
            return None
        return await self.repo.get_random_message(message_group_choice.group_id)

    async def create_default_message_group_choices(
        self, channel_id: int
    ) -> list[MessageGroupChoice]:
        already_registered = await self.repo.channel_has_choices(channel_id)
        if already_registered:
            raise ChannelAlreadyRegisteredError

        message_groups = await self.repo.get_message_groups_by_name(
            *DEFAULT_CHANNEL_MESSAGE_GROUPS.keys()
        )
        message_group_choices = [
            MessageGroupChoice(
                snowflake_id=channel_id,
                group_id=mg.id,
                weight=DEFAULT_CHANNEL_MESSAGE_GROUPS[mg.name],
                is_channel=True,
                created_by=self.bot.user.id,
            )
            for mg in message_groups
        ]
        self.repo.session.add_all(message_group_choices)
        return message_group_choices


class ChannelAlreadyRegisteredError(Exception):
    pass
