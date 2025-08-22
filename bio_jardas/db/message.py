from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bio_jardas.db.base import Base


class MessageGroup(Base):
    __tablename__ = "message_group"

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


class Message(Base):
    __tablename__ = "message"

    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    group_id: Mapped[int] = mapped_column(
        sa.ForeignKey("message_group.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group: Mapped["MessageGroup"] = relationship(
        back_populates="messages", lazy="raise"
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
