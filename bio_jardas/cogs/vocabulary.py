from dishka import FromDishka
from disnake.ext.commands import Context, check, command

from bio_jardas.cogs.base import BaseCog
from bio_jardas.cogs.reply import logger
from bio_jardas.command_checks import is_bot_owner
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.services.message import MessageService
from bio_jardas.shortcuts import author_id


class VocabularyCog(BaseCog):
    @command(name="vocabulary")
    @cog_inject
    async def add_vocabulary(
        self,
        context: Context,
        *,
        text: str,
        message_service: FromDishka[MessageService],
    ):
        reply = await message_service.add_vocabulary(
            text, "user_added_vocabulary", author_id(context)
        )
        await logger.ainfo(
            "Replied to added vocabulary",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(reply.text)

    @command(name="vocabulary_admin")
    @check(is_bot_owner)
    @cog_inject
    async def add_admin_vocabulary(
        self,
        context: Context,
        message_group_name: str,
        *,
        text: str,
        message_service: FromDishka[MessageService],
    ):
        reply = await message_service.add_vocabulary(
            text, message_group_name, author_id(context)
        )
        await logger.ainfo(
            "Replied to added vocabulary",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(reply.text)
