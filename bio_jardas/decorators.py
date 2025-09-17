from functools import wraps

from disnake import Message


def skip_bots_and_commands(func):
    @wraps(func)
    async def wrapper(self, message: Message, *args, **kwargs):
        if message.author.bot:
            return None

        context = await self.bot.get_context(message)
        if context.valid:
            return None

        return await func(self, message, *args, **kwargs)

    return wrapper
