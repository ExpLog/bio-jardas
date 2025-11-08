import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer
from disnake import Intents
from disnake.ext.commands import (
    Bot,
    CheckFailure,
    CommandError,
    CommandOnCooldown,
    Context,
)

from bio_jardas import emojis
from bio_jardas.observability import (
    bind_attempted_command,
    bind_command_context_to_logs,
)

logger = structlog.stdlib.get_logger()


class BioJardas(Bot):
    def __init__(self, scheduler: AsyncIOScheduler, *args, **kwargs):
        self.scheduler = scheduler
        self.container: AsyncContainer | None = None
        super().__init__(*args, **kwargs)

    async def on_ready(self) -> None:
        await logger.ainfo("BioJardas logged in as %s", self.user)
        await logger.ainfo("Starting scheduler")
        self.scheduler.start()
        await logger.ainfo("Scheduler started")

    @classmethod
    def build(cls, scheduler: AsyncIOScheduler) -> "BioJardas":
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        instance = cls(scheduler, command_prefix="$", intents=intents)
        instance.before_invoke(bind_command_context_to_logs)
        instance.before_message_command_invoke(bind_command_context_to_logs)
        instance.before_user_command_invoke(bind_command_context_to_logs)
        instance.before_slash_command_invoke(bind_command_context_to_logs)
        return instance

    def register_di_container(self, container: AsyncContainer) -> None:
        self.container = container

    async def on_command_error(self, context: Context, exception: CommandError) -> None:
        if self.extra_events.get("on_command_error", None):
            return

        if isinstance(exception, CommandOnCooldown):
            # command/cog error handler will still run if defined
            await context.message.add_reaction(emojis.WAIT)
            return

        if isinstance(exception, CheckFailure):
            await context.message.add_reaction(emojis.STOP)
            return

        command = context.command
        if command and command.has_error_handler():
            return

        cog = context.cog
        if cog and cog.has_error_handler():
            return

        await bind_command_context_to_logs(context)
        if not command:
            bind_attempted_command(context)

        await logger.awarning(
            "Ignoring error in command",
            exc_info=exception,
        )
        await context.message.add_reaction(emojis.UNKNOWN_ERROR)
