import asyncio

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bio_jardas.bot import BioJardas
from bio_jardas.dependency_injection import di_container
from bio_jardas.observability import (
    THIRD_PARTY_LOGGERS,
    instrument_logs,
)
from bio_jardas.settings import SETTINGS


async def main() -> None:
    instrument_logs(
        SETTINGS.log_level,
        extra_loggers=THIRD_PARTY_LOGGERS,
        force_console_renderer=SETTINGS.log_force_console_renderer,
    )

    logger = structlog.stdlib.get_logger()
    logger.info("Starting BioJardas")

    try:
        scheduler = await di_container.get(AsyncIOScheduler)
        scheduler.start()
        jardas = await di_container.get(BioJardas)
        jardas.register_di_container(di_container)
        await jardas.start(SETTINGS.discord.token)
    finally:
        await di_container.close()


if __name__ == "__main__":
    asyncio.run(main())
