from sqlalchemy import func, select

from bio_jardas.db import Message, MessageGroup, MessageGroupChoice
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.db.repositories.base import CRUDRepository


class MessageRepository(CRUDRepository[Message]):
    model_type = Message

    async def get_random(self, message_group_id: int) -> Message:
        """
        Get a random message from a message group.
        :param message_group_id: A MessageGroup.id.
        :return: A single message.
        """
        messages = await self.get_many(
            Message.group_id == message_group_id, order_by=[func.random()], limit=1
        )
        if not messages:
            raise EntityNotFoundError(Message, "random")
        return messages[0]


class MessageGroupRepository(CRUDRepository[MessageGroup]):
    model_type = MessageGroup

    async def get_assigned_message_groups(
        self, snowflake_id: int
    ) -> list[MessageGroup]:
        """
        Get the MessageGroups that are assigned to the snowflake_id through a
        MessageGroupChoice.
        :param snowflake_id: Discord snowflake id of a channel or user.
        :return: List of message groups.
        """
        query = (
            select(MessageGroup)
            .join(MessageGroupChoice)
            .where(MessageGroupChoice.snowflake_id == snowflake_id)
        )
        return list((await self.session.scalars(query)).all())


class MessageGroupChoiceRepository(CRUDRepository[MessageGroupChoice]):
    model_type = MessageGroupChoice
