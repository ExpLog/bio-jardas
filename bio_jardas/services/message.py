import random

import structlog
from disnake.ext.commands import Bot
from structlog.contextvars import bind_contextvars

from bio_jardas.db import Message, MessageGroup, MessageGroupChoice
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.db.repositories.message import MessageRepo
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
    def __init__(self, bot: Bot, repo: MessageRepo):
        self.bot = bot
        self.repo = repo

    async def random_message_group_choice(
        self, user_id: int, channel_id: int
    ) -> MessageGroupChoice | None:
        choices = await self.repo.get_message_group_choices(user_id, channel_id)
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

    async def random_reply(self, user_id: int, channel_id: int) -> Message | None:
        message_group_choice = await self.random_message_group_choice(
            user_id, channel_id
        )
        if not message_group_choice:
            return None
        bind_contextvars(roll_type=message_group_choice.roll_type)
        return await self.repo.get_random_message(message_group_choice.group_id)

    async def random_reply_from_group(self, message_group_name: str):
        message_groups = await self.repo.get_message_groups(names=[message_group_name])
        message_group = first(message_groups)
        if not message_group:
            raise EntityNotFoundError(MessageGroup, message_group_name)
        return await self.repo.get_random_message(message_group.id)

    async def apply_defaults_to_channel(
        self, channel_id: int
    ) -> list[MessageGroupChoice]:
        has_choices = await self.repo.channel_has_choices(channel_id)
        if has_choices:
            raise ChannelHasMessageGroupsError

        message_groups = await self.repo.get_message_groups(
            names=list(DEFAULT_CHANNEL_MESSAGE_GROUPS.keys())
        )
        message_group_choices = [
            MessageGroupChoice(
                snowflake_id=channel_id,
                group_id=mg.id,
                weight=DEFAULT_CHANNEL_MESSAGE_GROUPS[mg.name],
                is_channel=True,
                last_modified_by=self.bot.user.id,
            )
            for mg in message_groups
        ]
        self.repo.session.add_all(message_group_choices)
        return message_group_choices

    async def add_or_update_message_group_choice(self, dto: UpsertMessageGroupChoice):
        message_groups = await self.repo.get_message_groups(names=[dto.group_name])
        message_group = first(message_groups)
        if not message_group:
            raise EntityNotFoundError(MessageGroup, dto.group_name)

        message_group_choices = await self.repo.get_message_group_choices(
            dto.snowflake_id, group_name=message_group.name, for_update=True
        )
        message_group_choice = first(message_group_choices)
        if not message_group_choice:
            message_group_choice = MessageGroupChoice(
                snowflake_id=dto.snowflake_id,
                group=message_group,
                is_channel=dto.is_channel,
                is_user=dto.is_user,
            )
            self.repo.session.add(message_group_choice)

        message_group_choice.weight = dto.weight
        message_group_choice.independent_roll_probability = (
            dto.independent_roll_probability
        )
        message_group_choice.last_modified_by = dto.last_modified_by
        return message_group_choice


class ChannelHasMessageGroupsError(JardasError):
    def __init__(self):
        super().__init__("Channel already assigned message groups")
