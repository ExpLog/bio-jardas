import random

import structlog
from disnake.ext.commands import Bot
from sqlalchemy import delete, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db import Message, MessageGroup, MessageGroupChoice

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
        self.session = session

    async def get_assigned_message_groups(
        self, snowflake_id: int
    ) -> list[MessageGroup]:
        query = (
            select(MessageGroup)
            .join(MessageGroupChoice)
            .where(MessageGroupChoice.snowflake_id == snowflake_id)
        )
        return list((await self.session.scalars(query)).all())

    async def get_random_message_group_choice(
        self, user_id: int, channel_id: int
    ) -> MessageGroupChoice | None:
        query = select(MessageGroupChoice).where(
            MessageGroupChoice.snowflake_id.in_((user_id, channel_id))
        )
        weights = (await self.session.scalars(query)).all()
        if not weights:
            await logger.awarning(
                "Found 0 MessageGroupChoices",
                author_id=user_id,
                channel_id=channel_id,
            )
            return None

        return random.choices(weights, [sw.weight for sw in weights])[0]

    async def get_random_message(self, message_group_id: int) -> Message:
        query = (
            select(Message)
            .where(Message.group_id == message_group_id)
            .order_by(func.random())
            .limit(1)
        )
        return await self.session.scalar(query)

    async def create_default_message_group_choices(
        self, channel_id: int
    ) -> list[MessageGroupChoice]:
        already_registered_query = select(
            exists(MessageGroupChoice).where(
                MessageGroupChoice.snowflake_id == channel_id
            )
        )
        already_registered = await self.session.scalar(already_registered_query)
        if already_registered:
            raise ChannelAlreadyRegisteredError

        query = select(MessageGroup).where(
            MessageGroup.name.in_(DEFAULT_CHANNEL_MESSAGE_GROUPS.keys())
        )
        message_groups = (await self.session.scalars(query)).all()
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
        self.session.add_all(message_group_choices)
        return message_group_choices

    async def delete_message_group_choices(
        self, snowflake_id: int, group_names: list[str] | None
    ) -> None:
        query = (
            delete(MessageGroupChoice)
            .where(MessageGroupChoice.snowflake_id == snowflake_id)
            .where(
                MessageGroupChoice.id.in_(
                    select(MessageGroup.id).where(MessageGroup.name.in_(group_names))
                )
            )
        )
        # TODO: return how many choices were deleted?
        await self.session.scalar(query)


class ChannelAlreadyRegisteredError(Exception):
    pass
