import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.domains.message.models import (
    ChannelEnabled,
    Message,
    MessageGroup,
    MessageGroupChoice,
)
from bio_jardas.domains.message.repositories import (
    ChannelEnabledRepository,
    MessageGroupChoiceRepository,
    MessageGroupRepository,
    MessageRepository,
)


@pytest.fixture
async def message_repo(session: AsyncSession) -> MessageRepository:
    return MessageRepository(session)


@pytest.fixture
async def message_group_repo(session: AsyncSession) -> MessageGroupRepository:
    return MessageGroupRepository(session)


@pytest.fixture
async def message_group_choice_repo(
    session: AsyncSession,
) -> MessageGroupChoiceRepository:
    return MessageGroupChoiceRepository(session)


@pytest.fixture
async def channel_enabled_repo(session: AsyncSession) -> ChannelEnabledRepository:
    return ChannelEnabledRepository(session)


async def test_message_get_random(
    message_repo: MessageRepository, message_group_repo: MessageGroupRepository
) -> None:
    group = MessageGroup(name="test_group", created_by=0, updated_by=0)
    await message_group_repo.add(group)

    messages = [
        Message(text="msg1", group_id=group.id, created_by=0, updated_by=0),
        Message(text="msg2", group_id=group.id, created_by=0, updated_by=0),
    ]
    await message_repo.add_many(messages)

    random_msg = await message_repo.get_random(group.id)

    assert random_msg.text in ["msg1", "msg2"]
    assert random_msg.group_id == group.id


async def test_message_get_random_empty(message_repo: MessageRepository) -> None:
    with pytest.raises(EntityNotFoundError):
        await message_repo.get_random(999)


async def test_message_get_random_by_group_name(
    message_repo: MessageRepository, message_group_repo: MessageGroupRepository
) -> None:
    group = MessageGroup(name="test_group_name", created_by=0, updated_by=0)
    await message_group_repo.add(group)

    msg = Message(text="msg_by_name", group_id=group.id, created_by=0, updated_by=0)
    await message_repo.add(msg)

    random_msg = await message_repo.get_random_by_group_name("test_group_name")

    assert random_msg.text == "msg_by_name"
    assert random_msg.group_id == group.id


async def test_message_get_random_by_group_name_empty(
    message_repo: MessageRepository,
) -> None:
    with pytest.raises(EntityNotFoundError):
        await message_repo.get_random_by_group_name("non_existent_group")


async def test_message_group_get_assigned_message_groups(
    message_group_repo: MessageGroupRepository,
    message_group_choice_repo: MessageGroupChoiceRepository,
) -> None:
    group1 = MessageGroup(name="group1", created_by=0, updated_by=0)
    group2 = MessageGroup(name="group2", created_by=0, updated_by=0)
    await message_group_repo.add_many([group1, group2])

    snowflake_id = 12345
    choice = MessageGroupChoice(
        snowflake_id=snowflake_id, group_id=group1.id, created_by=0, updated_by=0
    )
    await message_group_choice_repo.add(choice)

    assigned_groups = await message_group_repo.get_assigned_message_groups(snowflake_id)

    assert len(assigned_groups) == 1
    assert assigned_groups[0].id == group1.id
    assert assigned_groups[0].name == "group1"


async def test_message_group_choice_crud(
    message_group_choice_repo: MessageGroupChoiceRepository,
    message_group_repo: MessageGroupRepository,
) -> None:
    group = MessageGroup(name="crud_group", created_by=0, updated_by=0)
    await message_group_repo.add(group)

    choice = MessageGroupChoice(
        snowflake_id=98765, group_id=group.id, weight=2.0, created_by=0, updated_by=0
    )
    await message_group_choice_repo.add(choice)

    fetched = await message_group_choice_repo.get_by_id(choice.id)
    assert fetched.weight == 2.0
    assert fetched.snowflake_id == 98765


async def test_channel_enabled_is_channel_enabled_query(
    channel_enabled_repo: ChannelEnabledRepository, session: AsyncSession
) -> None:
    channel_id = 55555
    enabled = ChannelEnabled(
        channel_snowflake_id=channel_id, created_by=0, updated_by=0
    )
    await channel_enabled_repo.add(enabled)

    # Test enabled channel
    query_enabled = channel_enabled_repo.is_channel_enabled_query(channel_id)
    result_enabled = await session.scalar(select(query_enabled))
    assert result_enabled is True

    # Test disabled channel
    query_disabled = channel_enabled_repo.is_channel_enabled_query(99999)
    result_disabled = await session.scalar(select(query_disabled))
    assert result_disabled is False
