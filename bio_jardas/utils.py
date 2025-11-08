from collections.abc import Sequence

import inflect
from disnake import Color, Embed
from whenever import ZonedDateTime

INFLECT = inflect.engine()


def first[T](sequence: Sequence[T] | None) -> T | None:
    return sequence[0] if sequence else None


def probability_as_percentage(probability: float) -> str:
    return f"{round(probability, 4) * 100}%"


def standard_embed(
    title: str, description: str | None = None, color: Color | None = None
) -> Embed:
    now = ZonedDateTime.now_in_system_tz()
    return Embed(
        title=title,
        description=description,
        color=color or Color.green(),
        timestamp=now.py_datetime(),
    )


def snake_case_to_title(string: str) -> str:
    return " ".join(part.capitalize() for part in string.split("_"))


def mention_by_snowflake_id(snowflake_id: int) -> str:
    return f"<@{snowflake_id}>"
