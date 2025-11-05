from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

import sqlalchemy as sa
from sqlalchemy import BigInteger, Identity
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry
from whenever import ZonedDateTime

from bio_jardas.db.types import ZonedDateTimeType
from bio_jardas.settings import SETTINGS

metadata = sa.MetaData()
mapper_registry = registry()
mapper_registry.type_annotation_map[ZonedDateTime] = ZonedDateTimeType()


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata
    registry = mapper_registry

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)


class TimestampMixin:
    created_at: Mapped[ZonedDateTime] = mapped_column(
        nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[ZonedDateTime] = mapped_column(
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


class AuditBase(Base, TimestampMixin):
    __abstract__ = True
    created_by: Mapped[int] = mapped_column(
        sa.BigInteger,
        nullable=False,
        comment="Snowflake id of the user. 0 for legacy.",
    )
    updated_by: Mapped[int] = mapped_column(
        sa.BigInteger,
        nullable=False,
        comment="Snowflake id of the user. 0 for legacy.",
    )


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
