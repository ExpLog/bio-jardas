import asyncio
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from cyclopts import App
from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.stdlib import get_logger

from bio_jardas.db import Message, MessageGroup
from bio_jardas.db.base import Session

logger = get_logger()
app = App(name="load csv")


class DatabaseNotEmptyError(Exception):
    pass


@dataclass(frozen=True)
class InsertedRows:
    message_groups: int
    messages: int


async def assert_no_data(session: AsyncSession) -> None:
    query = select(exists(MessageGroup))
    message_group_exists = await session.scalar(query)
    if message_group_exists:
        raise DatabaseNotEmptyError(
            "Database already contains message and message_group data."
            " This script only works with empty databases."
        )


async def load_csv(session: AsyncSession, csv_path: Path) -> InsertedRows:
    df = pd.read_csv(
        csv_path,
        usecols=["message_group", "text"],
        dtype={"message_group": "string", "text": "string"},
        keep_default_na=False,
    )

    # sanitize
    df["message_group"] = df["message_group"].str.strip()
    df["text"] = df["text"].str.strip()
    df = df[(df["message_group"] != "") & (df["text"] != "")]
    if df.empty:
        return InsertedRows(0, 0)

    df["message_group"].unique().tolist()
    message_group_names = df["message_group"].unique().tolist()
    message_groups = [MessageGroup(name=name) for name in message_group_names]
    session.add_all(message_groups)
    await session.flush()

    logger.info("Inserted %s rows into message_group.", len(message_groups))

    message_group_name_to_id = {g.name: g.id for g in message_groups}
    messages = [
        {"text": text, "group_id": message_group_name_to_id[group]}
        for group, text in df.itertuples(index=False)
    ]
    await session.execute(insert(Message), messages)
    logger.info("Inserted %s rows into message.", len(messages))

    return InsertedRows(len(message_group_names), len(messages))


async def load_data(csv: Path) -> None:
    async with Session() as session, session.begin():
        await assert_no_data(session)
        inserted_rows = await load_csv(session, csv)

    logger.info(
        "Inserted message group and messages into database",
        message_groups=inserted_rows.message_groups,
        messages=inserted_rows.messages,
    )


@app.default
def cli(csv: Path):
    """
    Load a CSV with columns: message_group, text into a blank DB.

    Args:
      csv: Path to CSV file.
    """
    try:
        asyncio.run(load_data(csv))
    except DatabaseNotEmptyError as ex:
        logger.error(str(ex))


if __name__ == "__main__":
    app()
