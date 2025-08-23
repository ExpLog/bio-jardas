import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db.config import Config
from bio_jardas.dtos.config import ReplyIntensityConfig

logger = structlog.stdlib.get_logger()


class ConfigService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_intensity(self) -> ReplyIntensityConfig:
        query = select(Config).where(Config.name == "intensity")
        config = await self.session.scalar(query)
        if config:
            return ReplyIntensityConfig(**config.data)
        return ReplyIntensityConfig()
