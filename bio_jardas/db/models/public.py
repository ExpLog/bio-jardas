from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from whenever import ZonedDateTime

from bio_jardas.db.base import AuditBase, Base, TimestampMixin
from bio_jardas.db.types import EnumString
from bio_jardas.domains.time_gate.enums import TimeGateNameEnum
from bio_jardas.domains.time_gate.exceptions import TimeGatedError
from bio_jardas.domains.time_gate.strategies import TimeGateStrategy


# TODO: change name of table/class to bot_config
class Config(AuditBase):
    __tablename__ = "config"

    name: Mapped[str] = mapped_column(nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")


class TimeGate(Base, TimestampMixin):
    __tablename__ = "time_gate"
    __table_args__ = (sa.UniqueConstraint("name", "user_snowflake_id"),)

    name: Mapped[TimeGateNameEnum] = mapped_column(
        EnumString(TimeGateNameEnum, 100), nullable=False
    )
    user_snowflake_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    resets_at: Mapped[ZonedDateTime] = mapped_column(
        nullable=False, default=ZonedDateTime.now_in_system_tz
    )

    def is_locked(self, now: ZonedDateTime | None = None) -> bool:
        now = now or ZonedDateTime.now_in_system_tz()
        return now < self.resets_at

    @contextmanager
    def lock(self):
        now = ZonedDateTime.now_in_system_tz()
        if self.is_locked(now):
            raise TimeGatedError(self.name, self.user_snowflake_id)

        strategy = TimeGateStrategy.get(self.name)
        try:
            yield self
        finally:
            strategy.lock_gate(self, now)
