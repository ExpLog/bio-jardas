from collections.abc import AsyncGenerator
from typing import Any

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.base import wrap_injection
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.bot import BioJardas
from bio_jardas.db.base import transaction
from bio_jardas.db.repositories.message import (
    MessageGroupChoiceRepository,
    MessageGroupRepository,
    MessageRepository,
)
from bio_jardas.services.config import ConfigService
from bio_jardas.services.message import MessageService


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    async def bot(self) -> BioJardas:
        from bio_jardas.cogs import ALL_COGS  # noqa: PLC0415

        bot = BioJardas.build()
        for cog in ALL_COGS:
            bot.add_cog(cog(bot))
        return bot


class AsyncSessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def transaction(self) -> AsyncGenerator[AsyncSession, Any]:
        async with transaction() as session:
            yield session


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide()
    async def message_repository(self, session: AsyncSession) -> MessageRepository:
        return MessageRepository(session)

    @provide()
    async def message_group_repository(
        self, session: AsyncSession
    ) -> MessageGroupRepository:
        return MessageGroupRepository(session)

    @provide()
    async def message_group_choice_repository(
        self, session: AsyncSession
    ) -> MessageGroupChoiceRepository:
        return MessageGroupChoiceRepository(session)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide()
    async def message_service(
        self,
        bot: BioJardas,
        message_repo: MessageRepository,
        group_repo: MessageGroupRepository,
        choice_repo: MessageGroupChoiceRepository,
    ) -> MessageService:
        return MessageService(bot, message_repo, group_repo, choice_repo)

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
