from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bio_jardas.db.base import Base


class MessageGroup(Base):
    __tablename__ = "message_group"
    __table_args__ = {"schema": "message"}

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(
        sa.String(1000), nullable=False, default="", server_default="''"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    available_choices: Mapped[list["MessageGroupChoice"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    created_by: Mapped[int] = mapped_column(
        sa.BigInteger,
        nullable=False,
        comment="Snowflake id of the user. 0 for legacy.",
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
    __table_args__ = {"schema": "message"}

    text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    group_id: Mapped[int] = mapped_column(
        sa.ForeignKey("message.message_group.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group: Mapped["MessageGroup"] = relationship(
        back_populates="messages", lazy="raise"
    )

    created_by: Mapped[int] = mapped_column(
        sa.BigInteger,
        nullable=False,
        comment="Snowflake id of the user. 0 for legacy.",
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


class MessageGroupChoice(Base):
    __tablename__ = "message_group_choice"
    __table_args__ = (
        sa.UniqueConstraint("snowflake_id", "group_id"),
        {"schema": "message"},
    )

    # snowflake_id can be a user/channel/whatever
    # they are guaranteed by discord to be unique
    # however, child objects may share a snowflake id with their parents
    snowflake_id: Mapped[int] = mapped_column(
        # index is covered by the unique (user_snowflake_id, group_id)
        sa.BigInteger,
        nullable=False,
    )
    group_id: Mapped[int] = mapped_column(
        sa.ForeignKey("message.message_group.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group: Mapped["MessageGroup"] = relationship(
        back_populates="available_choices", lazy="raise"
    )
    weight: Mapped[float] = mapped_column(
        nullable=False, default=1.0, server_default="1.0"
    )
    is_channel: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="false",
        comment="Whether the snowflake_id refers to a channel",
    )
    is_user: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="false",
        comment="Whether the snowflake_id refers to a user",
    )

    created_by: Mapped[int] = mapped_column(
        sa.BigInteger,
        nullable=False,
        comment="Snowflake id of the user. 0 for legacy.",
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
