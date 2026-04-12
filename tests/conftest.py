import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bio_jardas.settings import SETTINGS


@pytest.fixture(scope="session")
async def _engine():
    engine = create_async_engine(SETTINGS.postgres.url)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")

    def run_upgrade():
        command.upgrade(alembic_cfg, "head")

    await asyncio.to_thread(run_upgrade)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(_engine) -> AsyncGenerator[AsyncSession, Any]:
    """
    Fixture that yields an AsyncSession and rolls back at the end.
    Uses a transaction for each test to keep DB clean.
    """
    async with _engine.connect() as conn:
        # Start a transaction
        trans = await conn.begin()

        # Create a session bound to the connection
        session_factory = async_sessionmaker(conn, expire_on_commit=False)
        async with session_factory() as session:
            yield session

        # Roll back everything after the test
        await trans.rollback()
