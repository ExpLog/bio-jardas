import sqlalchemy as sa
from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry
from whenever import Instant
from whenever_sqlalchemy import type_annotation_map as whenever_type_map

metadata = sa.MetaData()
mapper_registry = registry()
mapper_registry.type_annotation_map.update(whenever_type_map)


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata
    registry = mapper_registry

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)


class TimestampMixin:
    created_at: Mapped[Instant] = mapped_column(
        nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[Instant] = mapped_column(
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
