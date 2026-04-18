import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.domains.config.models import Intensity
from bio_jardas.domains.config.objects import ReplyIntensityEnum
from bio_jardas.domains.config.repositories import IntensityRepository


@pytest.fixture
async def intensity_repo(session: AsyncSession) -> IntensityRepository:
    return IntensityRepository(session)


async def test_intensity_add_and_get(intensity_repo: IntensityRepository) -> None:
    channel_id = 123456789
    intensity_val = ReplyIntensityEnum.INTENSE

    new_intensity = Intensity(
        channel_snowflake_id=channel_id,
        intensity=intensity_val,
        created_by=0,
        updated_by=0,
    )
    await intensity_repo.add(new_intensity)

    fetched = await intensity_repo.get_one_or_none(
        Intensity.channel_snowflake_id == channel_id
    )

    assert fetched is not None
    assert fetched.channel_snowflake_id == channel_id
    assert fetched.intensity == intensity_val


async def test_intensity_unique_constraint(intensity_repo: IntensityRepository) -> None:
    channel_id = 123456789

    i1 = Intensity(
        channel_snowflake_id=channel_id,
        intensity=ReplyIntensityEnum.NORMAL,
        created_by=0,
        updated_by=0,
    )
    await intensity_repo.add(i1)

    i2 = Intensity(
        channel_snowflake_id=channel_id,
        intensity=ReplyIntensityEnum.INTENSE,
        created_by=0,
        updated_by=0,
    )

    with pytest.raises(IntegrityError):
        await intensity_repo.add(i2, flush=True)
