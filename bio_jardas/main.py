from __future__ import annotations

import structlog
from disnake import Intents
from disnake.ext.commands import Bot, Context

from bio_jardas.cogs import ExampleCog
from bio_jardas.observability import (
    THIRD_PARTY_LOGGERS,
    instrument_logs,
)


class BioJardas(Bot):
    async def on_ready(self):
        logger.info(f"BioJardas logged in as {self.user}")

    @classmethod
    def build(cls):
        intents = Intents.default()
        intents.message_content = True
        return cls(command_prefix="$", intents=intents)

    async def invoke(self, ctx: Context) -> None:
        pass


if __name__ == "__main__":
    from bio_jardas.settings import SETTINGS

    instrument_logs(
        SETTINGS.log_level,
        extra_loggers=THIRD_PARTY_LOGGERS,
    )

    logger = structlog.get_logger()
    logger.info("Starting BioJardas")
    jardas = BioJardas.build()
    jardas.add_cog(ExampleCog())
    jardas.run(SETTINGS.discord.token)
