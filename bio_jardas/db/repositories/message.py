from sqlalchemy import delete, exists, func, select

from bio_jardas.db import Message, MessageGroup, MessageGroupChoice
from bio_jardas.db.repositories.base import Repository


class MessageRepo(Repository):
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

    async def get_message_groups_by_name(self, *name: str) -> list[MessageGroup]:
        """
        Get MessageGroups by their name.
        :param name: Name of the message group.
        :return: List of message groups.
        """
        query = select(MessageGroup).where(MessageGroup.name.in_(name))
        return list((await self.session.scalars(query)).all())

    async def get_message_group_choices(
        self, *snowflake_id: int
    ) -> list[MessageGroupChoice]:
        """
        Get the MessageGroupChoices for the given snowflake ids.
        :param snowflake_id: Discord snowflake id of a channel or user.
        :return: List of message group choices.
        """
        query = select(MessageGroupChoice).where(
            MessageGroupChoice.snowflake_id.in_(snowflake_id)
        )
        return list((await self.session.scalars(query)).all())

    async def delete_message_group_choices(
        self, snowflake_id: int, group_names: list[str] | None
    ) -> int:
        """
        Delete the MessageGroupChoices for the given snowflake id.
        :param snowflake_id: Discord snowflake id of a channel or user.
        :param group_names: Filter which choices get deleted by name.
        :return: How many MessageGroupChoice were deleted.
        """
        query = delete(MessageGroupChoice).where(
            MessageGroupChoice.snowflake_id == snowflake_id
        )
        if group_names:
            query = query.where(
                MessageGroupChoice.group_id.in_(
                    select(MessageGroup.id).where(MessageGroup.name.in_(group_names))
                )
            )
        result = await self.session.execute(query)
        return result.rowcount

    async def channel_has_choices(self, channel_id: int) -> bool:
        """
        Checks if a channel has assigned MessageGroupChoices without fetching them.
        :param channel_id: Discord snowflake id of a channel.
        :return: A boolean.
        """
        query = select(
            exists(MessageGroupChoice).where(
                MessageGroupChoice.snowflake_id == channel_id
            )
        )
        return await self.session.scalar(query)

    async def get_random_message(self, message_group_id: int) -> Message:
        """
        Get a random message from a message group.
        :param message_group_id: A MessageGroup.id.
        :return: A single message.
        """
        query = (
            select(Message)
            .where(Message.group_id == message_group_id)
            .order_by(func.random())
            .limit(1)
        )
        return await self.session.scalar(query)
