import structlog
from dishka import FromDishka
from disnake import Member  # Ensure Member is imported
from disnake.ext.commands import Context, command

from bio_jardas.cogs import BaseCog
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.message.services import MessageService

logger = structlog.stdlib.get_logger()


class HugCog(BaseCog):
    @command(name="huggies")
    @cog_inject
    async def hug(
        self,
        context: Context,
        *,
        message_service: FromDishka[MessageService],
    ):
        reply = await message_service.random_message_from_group("hug")
        await logger.ainfo(
            "Replied to hug",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(f"{context.author.mention}, this is for you")
        await context.channel.send(reply.text)

    @command(name="send_hugs")
    @cog_inject
    async def send_hugs(
        self,
        context: Context,
        member: Member | None = None,
        *,
        message_service: FromDishka[MessageService],
    ):
        target = member if member else context.author
        reply = await message_service.random_message_from_group("hug")
        await logger.ainfo(
            "Sent hug",
            target_user_id=target.id,
            target_user_name=target.name,
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(
            f"{target.mention}, {reply.interpolate_mention(context.author.mention)}"
        )
