from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

import inflect
from disnake import Color, Embed

INFLECT = inflect.engine()


def first[T](sequence: Sequence[T] | None) -> T | None:
    return sequence[0] if sequence else None


def probability_as_percentage(probability: float) -> str:
    return f"{round(probability, 4) * 100}%"


def standard_embed(
    title: str, description: str | None = None, color: Color | None = None
) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=color or Color.green(),
        timestamp=datetime.now(tz=ZoneInfo("Europe/Lisbon")),
    )


def snake_case_to_title(string: str) -> str:
    return " ".join(part.capitalize() for part in string.split("_"))


def mention_by_snowflake_id(snowflake_id: int) -> str:
    return f"<@{snowflake_id}>"
