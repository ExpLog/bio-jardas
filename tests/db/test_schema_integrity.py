import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.domains.message.models import Message, MessageGroup, MessageGroupChoice


async def test_message_group_cascade_delete(session: AsyncSession) -> None:
    # Setup: Create a group with messages and choices
    group = MessageGroup(name="test_cascade", created_by=0, updated_by=0)
    session.add(group)
    await session.flush()

    message = Message(text="msg", group_id=group.id, created_by=0, updated_by=0)
    choice = MessageGroupChoice(
        snowflake_id=1, group_id=group.id, created_by=0, updated_by=0
    )
    session.add_all([message, choice])
    await session.flush()

    # Verify setup
    assert (
        await session.scalar(select(Message).where(Message.id == message.id))
    ) is not None
    assert (
        await session.scalar(
            select(MessageGroupChoice).where(MessageGroupChoice.id == choice.id)
        )
    ) is not None

    # Act: Delete the group
    await session.execute(delete(MessageGroup).where(MessageGroup.id == group.id))
    await session.flush()

    # Assert: Related records should be gone
    assert (
        await session.scalar(select(Message).where(Message.id == message.id))
    ) is None
    assert (
        await session.scalar(
            select(MessageGroupChoice).where(MessageGroupChoice.id == choice.id)
        )
    ) is None


async def test_foreign_key_constraint_violation(session: AsyncSession) -> None:
    # Act & Assert: Attempt to add a message with a non-existent group_id
    message = Message(text="invalid", group_id=999999, created_by=0, updated_by=0)
    session.add(message)

    with pytest.raises(IntegrityError):
        await session.flush()
