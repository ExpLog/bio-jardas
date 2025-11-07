import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from bio_jardas.domains.config.models import Config
from bio_jardas.domains.config.objects import ReplyIntensityConfig, ReplyIntensityEnum

logger = structlog.stdlib.get_logger()

REPLY_INTENSITY_MAP = {
    "sleep": ReplyIntensityEnum.SLEEPING,
    "puny": ReplyIntensityEnum.PUNY,
    "mild": ReplyIntensityEnum.MILD,
    "normal": ReplyIntensityEnum.NORMAL,
    "annoying": ReplyIntensityEnum.ANNOYING,
    "intense": ReplyIntensityEnum.INTENSE,
    "edgelord": ReplyIntensityEnum.EDGELORD,
}


class ConfigService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_intensity(self) -> ReplyIntensityConfig:
        # TODO: add some caching
        query = select(Config).where(Config.name == "intensity")
        config = await self.session.scalar(query)
        if not config:
            await logger.awarning("Config not found", config="intensity")
            return ReplyIntensityConfig()
        return ReplyIntensityConfig(**config.data)

    async def update_intensity(
        self, reply_intensity: ReplyIntensityEnum, user_id: int
    ) -> None:
        query = select(Config).where(Config.name == "intensity").with_for_update()
        config = await self.session.scalar(query)
        if config:
            config.data["intensity"] = reply_intensity
            config.updated_by = user_id
            flag_modified(config, "data")
            return

        await logger.awarning("Config not found, creating new one.", config="intensity")
        intensity_config = ReplyIntensityConfig(intensity=reply_intensity)
        config = Config(
            name="intensity",
            data=intensity_config.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        self.session.add(config)
