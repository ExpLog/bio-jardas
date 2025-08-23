import random

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db import Message, MessageGroup, MessageGroupChoice

logger = structlog.stdlib.get_logger()


class MessageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def select_message_group_choice(
        self, user_id: int, channel_id: int
    ) -> MessageGroupChoice | None:
        query = (
            select(MessageGroupChoice)
            .join(MessageGroup)
            .where(MessageGroupChoice.snowflake_id.in_((user_id, channel_id)))
        )
        weights = (await self.session.scalars(query)).all()
        if not weights:
            await logger.awarning(
                "Found 0 MessageGroupChoices",
                author_id=user_id,
                channel_id=channel_id,
            )
            # TODO: add default choice
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
