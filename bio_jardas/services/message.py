import random
from collections.abc import Sequence

import structlog
from disnake.ext.commands import Bot
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from structlog.contextvars import bind_contextvars

from bio_jardas.db import Message, MessageGroup, MessageGroupChoice
from bio_jardas.db.repositories.message import (
    MessageGroupChoiceRepository,
    MessageGroupRepository,
    MessageRepository,
)
from bio_jardas.domain_objects.message import MessageGroupProbabilities
from bio_jardas.dtos.message import UpsertMessageGroupChoice
from bio_jardas.exceptions import JardasError
from bio_jardas.utils import first

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
    def __init__(
        self,
        bot: Bot,
        msg_repo: MessageRepository,
        group_repo: MessageGroupRepository,
        choice_repo: MessageGroupChoiceRepository,
    ):
        self.bot = bot
        self.msg_repo = msg_repo
        self.group_repo = group_repo
        self.choice_repo = choice_repo

    async def random_message_group_choice(
        self, user_id: int, channel_id: int
    ) -> MessageGroupChoice | None:
        choices = await self.choice_repo.get_many(
            MessageGroupChoice.snowflake_id.in_((user_id, channel_id))
        )
        if not choices:
            return None

        independent_choices = [c for c in choices if c.is_independent_roll]
        for choice in independent_choices:
            if random.random() <= choice.independent_roll_probability:
                return choice

        weighted_choices = [c for c in choices if c.is_weighted_roll]
        return first(
            random.choices(weighted_choices, [c.weight for c in weighted_choices])
        )

    async def random_message(self, user_id: int, channel_id: int) -> Message | None:
        message_group_choice = await self.random_message_group_choice(
            user_id, channel_id
        )
        if not message_group_choice:
            return None
        bind_contextvars(roll_type=message_group_choice.roll_type)
        return await self.msg_repo.get_random(message_group_choice.group_id)

    async def random_reply_from_group(self, message_group_name: str):
        message_group = await self.group_repo.get_one(
            MessageGroup.name == message_group_name
        )
        return await self.msg_repo.get_random(message_group.id)

    async def apply_defaults_to_channel(
        self, channel_id: int, author_id: int
    ) -> list[MessageGroupChoice]:
        has_choices = await self.choice_repo.exists(
            MessageGroupChoice.snowflake_id == channel_id
        )
        if has_choices:
            raise ChannelHasMessageGroupsError

        message_groups = await self.group_repo.get_many(
            MessageGroup.name.in_(list(DEFAULT_CHANNEL_MESSAGE_GROUPS.keys()))
        )
        message_group_choices = [
            MessageGroupChoice(
                snowflake_id=channel_id,
                group_id=mg.id,
                weight=DEFAULT_CHANNEL_MESSAGE_GROUPS[mg.name],
                is_channel=True,
                created_by=author_id,
                updated_by=author_id,
            )
            for mg in message_groups
        ]
        return await self.choice_repo.add_many(message_group_choices)

    async def add_or_update_message_group_choice(self, dto: UpsertMessageGroupChoice):
        group = await self.group_repo.get_one(MessageGroup.name == dto.group_name)
        choice = await self.choice_repo.get_one_or_none(
            MessageGroupChoice.snowflake_id == dto.snowflake_id,
            MessageGroupChoice.group_id == group.id,
            for_update=True,
        )
        if not choice:
            choice = MessageGroupChoice(
                snowflake_id=dto.snowflake_id,
                group=group,
                is_channel=dto.is_channel,
                is_user=dto.is_user,
                weight=dto.weight,
                independent_roll_probability=dto.independent_roll_probability,
                created_by=dto.updated_by,
                updated_by=dto.updated_by,
            )
            await self.choice_repo.add(choice)
        else:
            choice.weight = dto.weight
            choice.independent_roll_probability = dto.independent_roll_probability
            choice.updated_by = dto.updated_by
        return choice

    async def reply_probabilities(
        self, snowflake_id: int
    ) -> list[MessageGroupProbabilities]:
        choices = await self.choice_repo.get_many(
            MessageGroupChoice.snowflake_id == snowflake_id,
            options=[joinedload(MessageGroupChoice.group)],
        )
        total_weight = sum(mgc.weight for mgc in choices)
        return [
            MessageGroupProbabilities(
                group_name=choice.group.name,
                weight=choice.weight,
                roll=choice.independent_roll_probability,
                total_weight=total_weight,
            )
            for choice in choices
        ]

    async def delete_message_group_choices(
        self, snowflake_id: int, group_names: Sequence[str] | None = None
    ) -> int:
        filters = [MessageGroupChoice.snowflake_id == snowflake_id]
        if group_names:
            filters.append(
                MessageGroupChoice.group_id.in_(
                    select(MessageGroup.id).where(MessageGroup.name.in_(group_names))
                )
            )
        return await self.choice_repo.delete_where(*filters)

    async def add_vocabulary(
        self, text: str, message_group_name: str, user_id: int
    ) -> Message:
        clean_text = text.strip().strip('"').strip("'")
        group = await self.group_repo.get_one(MessageGroup.name == message_group_name)
        message = Message(
            text=clean_text, group=group, created_by=user_id, updated_by=user_id
        )
        await self.msg_repo.add(message)
        await logger.ainfo(
            "Added new vocabulary",
            message_group_id=message.group_id,
            message_id=message.id,
        )
        return await self.msg_repo.get_random_by_group_name("vocabulary_added")


class ChannelHasMessageGroupsError(JardasError):
    def __init__(self):
        super().__init__("Channel already assigned message groups")
