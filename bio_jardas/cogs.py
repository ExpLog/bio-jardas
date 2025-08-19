from disnake.ext.commands import Bot, Cog, Context, command


class ExampleCog(Cog):
    @command()
    async def damn(self, ctx: Context[Bot]) -> None:
        await ctx.channel.send("DAMN!")

    @command()
    async def hello(self, ctx: Context[Bot]) -> None:
        message = ctx.message
        await ctx.channel.send(f"Hello, {message.author.mention}!")
