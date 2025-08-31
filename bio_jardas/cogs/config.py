from datetime import datetime
from zoneinfo import ZoneInfo

import structlog
from disnake import Color, Embed
from disnake.ext.commands import Bot, Cog, CommandError, Context, command

from bio_jardas import emojis
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
        async with transaction() as session:
            config_service = ConfigService(session)
            await config_service.update_intensity(ReplyIntensityEnum(new_intensity))
        await logger.ainfo("Intensity updated")
        await context.message.add_reaction(emojis.SUCCESS)

    @intensity.error
    async def intensity_error_handler(self, context: Context, exception: CommandError):
        await logger.ainfo("Failed to set new intensity", exception=str(exception))
        await context.message.add_reaction(emojis.FAILURE)

    @command()
    async def status(self, context: Context[Bot]):
        async with transaction() as session:
            config_service = ConfigService(session)
            intensity_config = await config_service.get_intensity()

            message_repo = MessageRepo(session)
            assigned_message_groups = await message_repo.get_assigned_message_groups(
                context.channel.id
            )

        embed = Embed(
            title="Status",
            color=Color.green(),
            timestamp=datetime.now(tz=ZoneInfo("Europe/Lisbon")),
        )
        embed.set_footer(text="Toss a coin to your Jardas")
        embed.add_field("Intensity", intensity_config.intensity)
        embed.add_field(
            "Reply%", f"{round(intensity_config.reply_probability(), 4) * 100}%"
        )
        if assigned_message_groups:
            message_groups_str = "\n".join(mg.name for mg in assigned_message_groups)
            embed.add_field(
                "Channel Message Groups", message_groups_str, inline=False
            )
        await context.send(embed=embed, reference=context.message)
