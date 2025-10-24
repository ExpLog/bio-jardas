import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from bio_jardas.db.base import Base, TimestampMixin


class Score(Base, TimestampMixin):
    __tablename__ = "score"
    __table_args__ = (
        sa.UniqueConstraint("name", "user_snowflake_id"),
        {"schema": "game"},
    )

    user_snowflake_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    current: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    highest: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")

    def increase_by(self, amount: int = 1):
        self.current += amount
        self.highest = max(self.current, self.highest)

    def reset(self):
        self.current = 0
