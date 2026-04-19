import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.domains.time_gate.enums import TimeGateNameEnum
from bio_jardas.domains.time_gate.models import TimeGate
from bio_jardas.domains.time_gate.repositories import TimeGateRepository


@pytest.fixture
async def time_gate_repo(session: AsyncSession) -> TimeGateRepository:
    return TimeGateRepository(session)


async def test_time_gate_get_or_create_new(time_gate_repo: TimeGateRepository) -> None:
    user_id = 123456789
    gate_name = TimeGateNameEnum.FORTUNE_TELLER

    gate = await time_gate_repo.get_or_create(gate_name, user_id)

    assert gate.user_snowflake_id == user_id
    assert gate.name == gate_name.value
    assert gate.id is not None


async def test_time_gate_get_or_create_existing(
    time_gate_repo: TimeGateRepository,
) -> None:
    user_id = 123456789
    gate_name = TimeGateNameEnum.FORTUNE_TELLER

    # Create first
    original = TimeGate(user_snowflake_id=user_id, name=gate_name)
    await time_gate_repo.add(original)

    # Get again
    fetched = await time_gate_repo.get_or_create(gate_name, user_id)

    assert fetched.id == original.id
    assert fetched.user_snowflake_id == user_id
    assert fetched.name == gate_name.value


async def test_time_gate_get_or_create_for_update(
    time_gate_repo: TimeGateRepository,
) -> None:
    user_id = 123456789
    gate_name = TimeGateNameEnum.FORTUNE_TELLER

    # Just ensure it doesn't crash
    gate = await time_gate_repo.get_or_create(gate_name, user_id, for_update=True)
    assert gate.user_snowflake_id == user_id
