import structlog
from disnake import Intents
from disnake.ext.commands import Bot, CommandError, Context

from bio_jardas.cogs.config import ConfigCog
from bio_jardas.cogs.message import MessageCog
from bio_jardas.observability import (
    THIRD_PARTY_LOGGERS,
    instrument_logs,
)
from bio_jardas.settings import SETTINGS


class BioJardas(Bot):
    async def on_ready(self) -> None:
        logger.info("BioJardas logged in as %s", self.user)

    @classmethod
    def build(cls) -> "BioJardas":
        intents = Intents.default()
        intents.message_content = True
        return cls(command_prefix="$", intents=intents)

    async def on_command_error(self, context: Context, exception: CommandError) -> None:
        if self.extra_events.get("on_command_error", None):
            return

        command = context.command
        if command and command.has_error_handler():
            return

        cog = context.cog
        if cog and cog.has_error_handler():
            return

        await logger.awarning(
            "Ignoring error in command",
            command=f"{cog.qualified_name}.{command.qualified_name}",
            exception=str(exception),
        )


if __name__ == "__main__":
    instrument_logs(
        SETTINGS.log_level,
        extra_loggers=THIRD_PARTY_LOGGERS,
    )

    logger = structlog.stdlib.get_logger()
    logger.info("Starting BioJardas")
    jardas = BioJardas.build()
    jardas.add_cog(MessageCog(jardas))
    jardas.add_cog(ConfigCog(jardas))
    jardas.run(SETTINGS.discord.token)
