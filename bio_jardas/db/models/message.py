"""
Message models.

Note that not all message groups are replies. Things like fortunes are also a message
group.

While this is a core construct of the bot, it's not a feature by itself. It's data
that's leveraged by actual features.
"""

from typing import Literal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bio_jardas.db.base import AuditBase


class MessageGroup(AuditBase):
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
    disabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False, server_default="false"
    )


class Message(AuditBase):
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

    disabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False, server_default="false"
    )

    def interpolate_mention(self, mention: str) -> str:
        text = self.text
        if "$mention" not in text:
            text = f"$mention, {text}"
        return text.replace("$mention", mention)


class MessageGroupChoice(AuditBase):
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

    # A MessageGroupChoice with weight > 0 is considered a weighted roll choice,
    # while one with independent_roll_probability in considered an independent roll
    # Independent rolls are rolled separately before the weighted rolls and will
    # short-circuit them.
    # For simplicity, a choice can have both weight and independent_roll_probability
    # this just means that it will be considered for both rolls
    weight: Mapped[float] = mapped_column(
        nullable=False,
        default=1.0,
        server_default="1.0",
        comment="Weighted roll choices are weighted between themselves",
    )
    independent_roll_probability: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        server_default="0.0",
        comment="Independent roll choices are rolled before weighted choices",
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

    disabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False, server_default="false"
    )

    @property
    def is_weighted_roll(self) -> float:
        return self.weight > 0

    @property
    def is_independent_roll(self) -> float:
        return self.independent_roll_probability > 0

    @property
    def roll_type(self) -> Literal["weighted", "independent", "all"]:
        if self.is_weighted_roll and self.is_independent_roll:
            return "all"
        if self.is_weighted_roll:
            return "weighted"
        return "independent"
