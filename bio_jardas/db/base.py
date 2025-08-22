import sqlalchemy as sa
from sqlalchemy import Identity
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from bio_jardas.settings import SETTINGS

metadata = sa.MetaData()


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)


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
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
