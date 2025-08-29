from textwrap import dedent

import structlog
from disnake.ext.commands import Bot, Cog, CommandError, Context, command

from bio_jardas.db.base import transaction
from bio_jardas.db.repositories.message import MessageRepo
from bio_jardas.dtos.config import ReplyIntensityEnum
from bio_jardas.services.config import ConfigService

logger = structlog.stdlib.get_logger()


class ConfigCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(help="|".join(ReplyIntensityEnum))
    async def intensity(
        self, context: Context[Bot], new_intensity: ReplyIntensityEnum
    ) -> None:
        author = context.author
        async with transaction() as session:
            config_service = ConfigService(session)
            await config_service.update_intensity(ReplyIntensityEnum(new_intensity))
        await logger.ainfo(
            "Intensity updated",
            author_id=author.id,
        )
        await context.message.add_reaction("✅")

    @intensity.error
    async def intensity_error_handler(self, context: Context, exception: CommandError):
        await logger.ainfo(
            "Failed to set new intensity",
            exception=str(exception),
            author_id=context.author.id,
        )
        await context.message.add_reaction("❌")

    @command()
    async def status(self, context: Context[Bot]):
        async with transaction() as session:
            config_service = ConfigService(session)
            intensity_config = await config_service.get_intensity()

            message_repo = MessageRepo(session)
            assigned_message_groups = await message_repo.get_assigned_message_groups(
                context.channel.id
            )

        message_groups_str = (
            ", ".join(mg.name for mg in assigned_message_groups)
            if assigned_message_groups
            else "none"
        )
        await context.reply(
            dedent(
                f"""
                intensity = {intensity_config.intensity}
                reply% = {round(intensity_config.reply_probability(), 4) * 100}%
                message groups = {message_groups_str}
            """
            )
        )
