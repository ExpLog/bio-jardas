from sqlalchemy import ColumnElement, delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from bio_jardas.db.base import Base
from bio_jardas.db.exceptions import EntityNotFoundError


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session


class CRUDRepository[T: Base]:
    model_type: type[T]

    def __init__(self, session: AsyncSession, flush: bool = True) -> None:
        self.session = session
        self._flush: bool = flush

    async def _flush_session(self, flush: bool | None = None):
        if self._flush or flush:
            await self.session.flush()

    def _check_not_found(self, instance: T | None, identifier: str) -> None:
        if not instance:
            raise EntityNotFoundError(self.model_type, identifier)

    async def add(self, entity: T, flush: bool | None = None) -> T:
        self.session.add(entity)
        await self._flush_session(flush)
        return entity

    async def add_many(self, entities: list[T], flush: bool | None = None) -> list[T]:
        self.session.add(entities)
        await self._flush_session(flush)
        return entities

    async def delete(self, entity_id: int) -> bool:
        query = delete(self.model_type).where(self.model_type.id == entity_id)
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def delete_many(self, entity_ids: list[int]) -> int:
        query = delete(self.model_type).where(self.model_type.id.in_(entity_ids))
        result = await self.session.execute(query)
        return result.rowcount

    async def delete_where(self, *filters: ColumnElement[bool]) -> int:
        query = delete(self.model_type).where(*filters)
        result = await self.session.execute(query)
        return result.rowcount

    async def exists(self, *filters: ColumnElement[bool]) -> bool:
        query = select(exists(self.model_type).where(*filters))
        return await self.session.scalar(query)

    async def get_by_id(
        self,
        instance_id: int,
        options: list[ExecutableOption] | None = None,
        for_update: bool = False,
    ) -> T:
        instance = await self.get_one_or_none(
            self.model_type.id == instance_id, options=options, for_update=for_update
        )
        self._check_not_found(instance, f"id={instance_id}")
        return instance

    async def get_one(
        self,
        *filters: ColumnElement[bool],
        options: list[ExecutableOption] | None = None,
        for_update: bool = False,
    ) -> T:
        instance = await self.get_one_or_none(
            *filters, options=options, for_update=for_update
        )
        # TODO: improve the identifier
        self._check_not_found(instance, "get_one")
        return instance

    async def get_one_or_none(
        self,
        *filters: ColumnElement[bool],
        options: list[ExecutableOption] | None = None,
        for_update: bool = False,
    ) -> T | None:
        query = select(self.model_type).where(*filters)
        if options:
            query = query.options(*options)
        if for_update:
            query = query.with_for_update()
        return await self.session.scalar(query)

    async def get_many(
        self,
        *filters: ColumnElement[bool],
        options: list[ExecutableOption] | None = None,
        for_update: bool = False,
    ) -> list[T]:
        query = select(self.model_type).where(*filters)
        if options:
            query = query.options(*options)
        if for_update:
            query = query.with_for_update()
        return list((await self.session.scalars(query)).all())
