import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from whenever import ZonedDateTime

from bio_jardas.db.base import AuditBase, Base, TimestampMixin


# TODO: change name of table/class to bot_config
class Config(AuditBase):
    __tablename__ = "config"

    name: Mapped[str] = mapped_column(nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")


class TimeGate(Base, TimestampMixin):
    __tablename__ = "time_gate"
    __table_args__ = (sa.UniqueConstraint("name", "user_snowflake_id"),)

    user_snowflake_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    resets_at: Mapped[ZonedDateTime] = mapped_column(nullable=False)
