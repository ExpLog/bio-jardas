from collections.abc import AsyncGenerator
from typing import Any

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.base import wrap_injection
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.bot import BioJardas
from bio_jardas.db.base import transaction
from bio_jardas.db.repositories.message import MessageRepo
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import MessageService


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    async def bot(self) -> BioJardas:
        from bio_jardas.cogs.config import ConfigCog  # noqa: PLC0415
        from bio_jardas.cogs.reply import ReplyCog  # noqa: PLC0415

        bot = BioJardas.build()
        bot.add_cog(ReplyCog(bot))
        bot.add_cog(ConfigCog(bot))
        return bot


class AsyncSessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def transaction(self) -> AsyncGenerator[AsyncSession, Any]:
        async with transaction() as session:
            yield session


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def message_repo(self, session: AsyncSession) -> MessageRepo:
        return MessageRepo(session)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide()
    async def message_service(
        self, bot: BioJardas, repo: MessageRepo
    ) -> MessageService:
        return MessageService(bot, repo)

    @provide()
    async def config_service(self, session: AsyncSession) -> ConfigService:
        return ConfigService(session)


def _get_di_cog_container(*args, **_kwargs) -> AsyncContainer:
    return args[0][0].container


def cog_inject(func):
    return wrap_injection(
        func=func,
        is_async=True,
        scope=Scope.REQUEST,
        container_getter=_get_di_cog_container,
    )


def build_di_container() -> AsyncContainer:
    return make_async_container(
        AsyncSessionProvider(), RepositoryProvider(), ServiceProvider(), BotProvider()
    )


di_container = build_di_container()
