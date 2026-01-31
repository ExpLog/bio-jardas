import random

import structlog
from dishka import FromDishka
from disnake import Member
from disnake.ext.commands import Context, dynamic_cooldown, group, BucketType

from bio_jardas.cogs import BaseCog
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.message.services import MessageService
from bio_jardas.guild_custom import jecs_cooldown

logger = structlog.stdlib.get_logger()


class RoastCog(BaseCog):
    @group(name="roast", invoke_without_command=True, case_insensitive=True)
    @cog_inject
    async def roast(
        self,
        context: Context,
        *,
        member: Member,
        message_service: FromDishka[MessageService],
    ) -> None:
        await _roast_target(context, member, message_service)

    @roast.command(name="me")
    @cog_inject
    async def roast_me(
        self, context: Context, *, message_service: FromDishka[MessageService]
    ) -> None:
        await _roast_target(context, context.author, message_service)

    @roast.command(name="random")
    @dynamic_cooldown(cooldown=jecs_cooldown, type=BucketType.user)
    @cog_inject
    async def roast_random(
        self, context: Context, *, message_service: FromDishka[MessageService]
    ) -> None:
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            target = random.choice(context.guild.members)
            if context.bot.user.id != target.id:
                await _roast_target(context, target, message_service)
                break
            attempts += 1


async def _roast_target(
    context: Context, target: Member, message_service: MessageService
):
    reply = await message_service.random_message_from_group("roast")
    await logger.ainfo(
        "Replied to roast",
        target_user_id=target.id,
        target_user_name=target.name,
        message_group_id=reply.group_id,
        message_id=reply.id,
    )
    await context.channel.send(reply.interpolate_mention(target.mention))
