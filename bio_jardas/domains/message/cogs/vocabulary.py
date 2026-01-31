from dishka import FromDishka
from disnake.ext.commands import Context, check, command

from bio_jardas import emojis
from bio_jardas.cogs import BaseCog
from bio_jardas.command_checks import is_bot_owner
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.message.cogs.reply import logger
from bio_jardas.domains.message.services import MessageService
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
        await context.message.add_reaction(emojis.SUCCESS)

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

    @command(name="add_message_group")
    @check(is_bot_owner)
    @cog_inject
    async def add_message_group(
        self,
        context: Context,
        message_group_name: str,
        *,
        message_service: FromDishka[MessageService],
    ):
        await message_service.add_message_group(message_group_name, author_id(context))
        await context.message.add_reaction(emojis.SUCCESS)
