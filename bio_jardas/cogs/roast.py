import structlog
from dishka import FromDishka
from disnake import Member
from disnake.ext.commands import Context, command

from bio_jardas.cogs.base import BaseCog
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.services.message import MessageService

logger = structlog.stdlib.get_logger()


class RoastCog(BaseCog):
    @command(name="roast")
    @cog_inject
    async def roast(
        self,
        context: Context,
        *,
        member: Member,
        message_service: FromDishka[MessageService],
    ):
        reply = await message_service.random_message_from_group("roast")
        await logger.ainfo(
            "Replied to roast",
            target_user_id=member.id,
            target_user_name=member.name,
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(reply.interpolate_mention(member.mention))
