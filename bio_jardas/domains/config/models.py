import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from bio_jardas.db.models import AuditBase

__all__ = ["Intensity"]


class Intensity(AuditBase):
    __tablename__ = "intensity"

    channel_snowflake_id: Mapped[int] = mapped_column(
        sa.BigInteger, nullable=False, unique=True, index=True
    )
    intensity: Mapped[str] = mapped_column(sa.String(100), nullable=False)
