from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates
from whenever import ZonedDateTime

from bio_jardas.db.models import Base, TimestampMixin
from bio_jardas.domains.time_gate.enums import TimeGateNameEnum
from bio_jardas.domains.time_gate.exceptions import TimeGatedError
from bio_jardas.domains.time_gate.strategies import TimeGateStrategy

__all__ = ["TimeGate"]


class TimeGate(Base, TimestampMixin):
    __tablename__ = "time_gate"
    __table_args__ = (sa.UniqueConstraint("name", "user_snowflake_id"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_snowflake_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    resets_at: Mapped[ZonedDateTime] = mapped_column(
        nullable=False, default=ZonedDateTime.now_in_system_tz
    )

    def is_locked(self, now: ZonedDateTime | None = None) -> bool:
        now = now or ZonedDateTime.now_in_system_tz()
        return now < self.resets_at

    @property
    def name_enum(self) -> TimeGateNameEnum:
        return TimeGateNameEnum(self.name)

    @validates("name")
    def _validate_name(self, _key, value):
        if isinstance(value, TimeGateNameEnum):
            return value.value
        return TimeGateNameEnum(value).value

    @contextmanager
    def lock(self):
        now = ZonedDateTime.now_in_system_tz()
        if self.is_locked(now):
            raise TimeGatedError(self.name, self.user_snowflake_id)

        strategy = TimeGateStrategy.get(self.name_enum)
        try:
            yield self
        finally:
            strategy.lock_gate(self, now)
