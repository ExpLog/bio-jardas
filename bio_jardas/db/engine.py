from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bio_jardas.settings import SETTINGS

engine = create_async_engine(
    SETTINGS.postgres.url,
    pool_size=SETTINGS.postgres.pool_size,
    max_overflow=SETTINGS.postgres.pool_max_overflow,
    pool_timeout=SETTINGS.postgres.pool_timeout,
    pool_recycle=SETTINGS.postgres.pool_recycle,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": SETTINGS.postgres.connection_timeout,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)
Session = async_sessionmaker(engine, expire_on_commit=False)


def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with Session() as session:
            async with session.begin():
                return await func(*args, **kwargs, session=session)

    return wrapper


@asynccontextmanager
async def transaction() -> AsyncGenerator[AsyncSession, Any]:
    async with Session() as session:
        async with session.begin():
            yield session
