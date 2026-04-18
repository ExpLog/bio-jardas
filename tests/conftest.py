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
    Uses a nested transaction for each test so database errors don't
    abort the main transaction, avoiding SAWarnings during cleanup.
    """
    async with _engine.connect() as conn:
        # Start the main transaction
        trans = await conn.begin()

        # Create a session bound to the connection
        session_factory = async_sessionmaker(conn, expire_on_commit=False)
        async with session_factory() as session:
            # Start a nested transaction (savepoint)
            # This allows tests to fail (e.g. IntegrityError) while keeping
            # the main transaction valid for rolling back.
            await session.begin_nested()
            yield session

        # Roll back the main transaction to keep the DB clean
        await trans.rollback()
