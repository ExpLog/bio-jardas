from disnake import Message
from disnake.ext.commands import Cooldown

from bio_jardas.shortcuts import author_id

JECS_SNOWFLAKE_ID = 192306440315076608


def jecs_cooldown(message: Message) -> Cooldown | None:
    if author_id(message) == JECS_SNOWFLAKE_ID:
        return Cooldown(1, 60)
    return None
