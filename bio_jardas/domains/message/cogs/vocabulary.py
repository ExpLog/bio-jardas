from dishka import FromDishka
from disnake.ext.commands import CommandError, Context, check, command
from structlog.contextvars import bind_contextvars

from bio_jardas import emojis
from bio_jardas.cogs import BaseCog
from bio_jardas.command_checks import is_bot_owner
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.message.cogs.reply import logger
from bio_jardas.domains.message.services import MessageService
from bio_jardas.observability import bind_attempted_command, bind_error_cause
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
        bind_attempted_command(context)
        bind_contextvars(target_message_group_name="user_added_vocabulary")

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
        bind_attempted_command(context)
        bind_contextvars(target_message_group_name=message_group_name)

        reply = await message_service.add_vocabulary(
            text, message_group_name, author_id(context)
        )
        await logger.ainfo(
            "Replied to added vocabulary",
            message_group_id=reply.group_id,
            message_id=reply.id,
        )
        await context.channel.send(reply.text)
        await context.message.add_reaction(emojis.SUCCESS)

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

    # local error handlers
    @add_vocabulary.error
    @add_admin_vocabulary.error
    async def add_vocabulary_error(self, context: Context, exception: CommandError):
        if isinstance(exception.__cause__, EntityNotFoundError):
            bind_error_cause(str(exception.__cause__))
            await logger.aerror(
                "Failed to add message to message group. Message group not found."
            )
            await context.message.add_reaction(emojis.NOT_FOUND)
