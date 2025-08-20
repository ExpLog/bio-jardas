import structlog
from disnake import Message
from disnake.ext.commands import Bot, Cog, Context, command

from bio_jardas.decorators import skip_bots_and_commands

logger = structlog.get_logger()


class ExampleCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def damn(self, ctx: Context[Bot]) -> None:
        await ctx.channel.send("DAMN!")

    @command()
    async def hello(self, ctx: Context[Bot]) -> None:
        message = ctx.message
        await ctx.channel.send(f"Hello, {message.author.mention}!")

    @Cog.listener("on_message")
    @skip_bots_and_commands
    async def reply(self, message: Message, *, context: Context[Bot]) -> None:
        await logger.ainfo("Message received", context_valid=context.valid)
        await message.reply("wat")


class Cog2(Cog):
    @command("do_it")
    async def do_it(self, ctx: Context[Bot]) -> None:
        await logger.ainfo("doing it")
        await ctx.message.reply("did it!")
