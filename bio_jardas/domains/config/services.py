import structlog

from bio_jardas.domains.config.models import Intensity
from bio_jardas.domains.config.objects import ReplyIntensityConfig, ReplyIntensityEnum
from bio_jardas.domains.config.repositories import IntensityRepository

logger = structlog.stdlib.get_logger()


class IntensityService:
    def __init__(self, repo: IntensityRepository):
        self.repo = repo

    async def get_intensity(self, channel_id: int) -> ReplyIntensityConfig:
        intensity_record = await self.repo.get_one_or_none(
            Intensity.channel_snowflake_id == channel_id
        )
        if not intensity_record:
            return ReplyIntensityConfig()
        return ReplyIntensityConfig(
            intensity=ReplyIntensityEnum(intensity_record.intensity)
        )

    async def update_intensity(
        self, channel_id: int, reply_intensity: ReplyIntensityEnum, user_id: int
    ) -> None:
        intensity_record = await self.repo.get_one_or_none(
            Intensity.channel_snowflake_id == channel_id,
            for_update=True,
        )
        if intensity_record:
            intensity_record.intensity = reply_intensity
            intensity_record.updated_by = user_id
            await self.repo.session.flush()
            return

        intensity_record = Intensity(
            channel_snowflake_id=channel_id,
            intensity=reply_intensity,
            created_by=user_id,
            updated_by=user_id,
        )
        await self.repo.add(intensity_record)
