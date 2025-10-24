from dishka import AsyncContainer
from disnake import Message
from disnake.ext.commands import Bot, Cog, Context

from bio_jardas.bot import BioJardas


class BaseCog(Cog):
    def __init__(self, bot: BioJardas):
        self.bot = bot

    @property
    def container(self) -> AsyncContainer:
        return self.bot.container

    async def get_message_context(self, message: Message) -> Context[Bot]:
        return await self.bot.get_context(message)
