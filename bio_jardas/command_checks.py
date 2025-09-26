from disnake.ext.commands import Context


async def is_bot_owner(context: Context) -> bool:
    return context.bot.owner.id == context.author.id
