from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from bio_jardas.db.base import AuditBase


# TODO: change name of table/class to bot_config
class Config(AuditBase):
    __tablename__ = "config"

    name: Mapped[str] = mapped_column(nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
