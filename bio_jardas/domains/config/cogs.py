import structlog
from dishka import FromDishka
from disnake.ext.commands import (
    Bot,
    BucketType,
    CommandError,
    Context,
    command,
    cooldown,
)

from bio_jardas import emojis
from bio_jardas.cogs import BaseCog
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.config.objects import ReplyIntensityEnum
from bio_jardas.domains.config.services import IntensityService
from bio_jardas.domains.message.repositories import MessageGroupRepository
from bio_jardas.observability import bind_exception_info
from bio_jardas.shortcuts import author_id, channel_id
from bio_jardas.utils import probability_as_percentage, standard_embed

logger = structlog.stdlib.get_logger()


class IntensityCog(BaseCog):
    @command(help="|".join(ReplyIntensityEnum))
    @cooldown(1, 10, BucketType.channel)
    @cog_inject
    async def intensity(
        self,
        context: Context[Bot],
        new_intensity: ReplyIntensityEnum,
        *,
        intensity_service: FromDishka[IntensityService],
    ) -> None:
        user_id = author_id(context)
        current_channel_id = channel_id(context)
        await intensity_service.update_intensity(
            current_channel_id, ReplyIntensityEnum(new_intensity), user_id
        )
        await logger.ainfo("Intensity updated", channel_id=current_channel_id)
        await context.message.add_reaction(emojis.SUCCESS)

    @intensity.error
    async def intensity_error_handler(self, context: Context, exception: CommandError):
        bind_exception_info(exception)
        await logger.aerror("Failed to set new intensity")
        await context.message.add_reaction(emojis.FAILURE)

    @command()
    @cog_inject
    async def status(
        self,
        context: Context[Bot],
        *,
        intensity_service: FromDishka[IntensityService],
        group_repo: FromDishka[MessageGroupRepository],
    ):
        current_channel_id = channel_id(context)
        intensity_config = await intensity_service.get_intensity(current_channel_id)
        assigned_message_groups = await group_repo.get_assigned_message_groups(
            current_channel_id
        )

        embed = standard_embed("Status")
        embed.set_footer(text="Toss a coin to your Jardas")
        embed.add_field("Intensity", intensity_config.intensity)
        embed.add_field(
            "Reply%", probability_as_percentage(intensity_config.reply_probability())
        )
        if assigned_message_groups:
            message_groups_str = "\n".join(mg.name for mg in assigned_message_groups)
            embed.add_field("Channel Message Groups", message_groups_str, inline=False)
        await context.send(embed=embed, reference=context.message)
