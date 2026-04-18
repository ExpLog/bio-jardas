import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.domains.config.objects import ReplyIntensityEnum
from bio_jardas.domains.config.repositories import IntensityRepository
from bio_jardas.domains.config.services import IntensityService


@pytest.fixture
async def intensity_service(session: AsyncSession) -> IntensityService:
    repo = IntensityRepository(session)
    return IntensityService(repo)


async def test_intensity_get_default(intensity_service: IntensityService) -> None:
    # No record for this channel
    config = await intensity_service.get_intensity(999)
    assert config.intensity == ReplyIntensityEnum.NORMAL


async def test_intensity_get_existing(intensity_service: IntensityService) -> None:
    channel_id = 111
    user_id = 222
    await intensity_service.update_intensity(
        channel_id, ReplyIntensityEnum.INTENSE, user_id
    )

    config = await intensity_service.get_intensity(channel_id)
    assert config.intensity == ReplyIntensityEnum.INTENSE


async def test_intensity_update_new(intensity_service: IntensityService) -> None:
    channel_id = 333
    user_id = 444
    await intensity_service.update_intensity(
        channel_id, ReplyIntensityEnum.EDGELORD, user_id
    )

    config = await intensity_service.get_intensity(channel_id)
    assert config.intensity == ReplyIntensityEnum.EDGELORD


async def test_intensity_update_existing(intensity_service: IntensityService) -> None:
    channel_id = 555
    user_id = 666

    # First set to NORMAL
    await intensity_service.update_intensity(
        channel_id, ReplyIntensityEnum.NORMAL, user_id
    )
    config = await intensity_service.get_intensity(channel_id)
    assert config.intensity == ReplyIntensityEnum.NORMAL

    # Now update to SLEEPING
    await intensity_service.update_intensity(
        channel_id, ReplyIntensityEnum.SLEEPING, user_id
    )
    config = await intensity_service.get_intensity(channel_id)
    assert config.intensity == ReplyIntensityEnum.SLEEPING
    assert config.reply_probability() == 0.0
