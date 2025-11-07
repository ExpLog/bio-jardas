import sqlalchemy as sa
from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry
from whenever import ZonedDateTime

from bio_jardas.db.types import ZonedDateTimeType

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
