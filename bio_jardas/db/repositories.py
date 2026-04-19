from collections.abc import Sequence

from sqlalchemy import ColumnElement, ColumnExpressionArgument, delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.db.models import Base


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session


class CRUDRepository[T: Base]:
    model_type: type[T]

    def __init__(self, session: AsyncSession, flush: bool = True) -> None:
        self.session = session
        self._flush: bool = flush

    async def _flush_session(self, flush: bool | None = None):
        flush = flush if flush is not None else self._flush
        if flush:
            await self.session.flush()

    def _check_not_found(self, instance: T | None, identifier: str) -> None:
        if not instance:
            raise EntityNotFoundError(self.model_type, identifier)

    async def add(self, entity: T, flush: bool | None = None) -> T:
        """
        Add entity to session.
        :param entity: Model instance.
        :param flush: Flush session. Overrides CRUDRepository flush setting if not None.
        :return: The same entity that was passed into the function.
        """
        self.session.add(entity)
        await self._flush_session(flush)
        return entity

    async def add_many(self, entities: list[T], flush: bool | None = None) -> list[T]:
        """
        Adds a list of entities to the session.
        :param entities: A list of model instances.
        :param flush: Flush session. Overrides CRUDRepository flush setting if not None.
        :return: The same list of entities that was passed into the function.
        """
        self.session.add_all(entities)
        await self._flush_session(flush)
        return entities

    async def delete(self, entity_id: int) -> bool:
        """
        Delete row by id.
        :param entity_id: The id of the entity to be deleted.
        :return: A row was deleted or not.
        """
        query = delete(self.model_type).where(self.model_type.id == entity_id)
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def delete_many(self, entity_ids: list[int]) -> int:
        """
        Delete many rows by id.
        :param entity_ids: The list of ids of the entities to be deleted.
        :return: How many rows were deleted.
        """
        query = delete(self.model_type).where(self.model_type.id.in_(entity_ids))
        result = await self.session.execute(query)
        return result.rowcount

    async def delete_where(self, *filters: ColumnElement[bool]) -> int:
        """
        Delete many rows by filters.
        :param filters: List of model filters.
        :return: How many rows were deleted.
        """
        query = delete(self.model_type).where(*filters)
        result = await self.session.execute(query)
        return result.rowcount

    async def exists(self, *filters: ColumnElement[bool]) -> bool:
        """
        Check if any row exists for the given list of filters.
        :param filters: List of model filters.
        :return: Rows exist or not.
        """
        query = select(exists(self.model_type).where(*filters))
        return await self.session.scalar(query)

    async def get_by_id(
        self,
        instance_id: int,
        options: list[ExecutableOption] | None = None,
        for_update: bool = False,
    ) -> T:
        """
        Get single model instance by id.
        :param instance_id: The id of the entity to be fetched.
        :param options: List of select.options, such as joinedload.
        :param for_update: Lock database rows for update.
        :return: Model instance. Raises EntityNotFoundError.
        """
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
        """
        Get single model instance by filters.
        :param filters: List of model filters.
        :param options: List of select.options, such as joinedload.
        :param for_update: Lock database rows for update.
        :return: Model instance. Raises EntityNotFoundError.
        """
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
        """
        Get single model instance or nothing by filters.
        :param filters: List of model filters.
        :param options: List of select.options, such as joinedload.
        :param for_update: Lock database rows for update.
        :return: Model instance or None. Raises EntityNotFoundError.
        """
        query = select(self.model_type).where(*filters)
        if options:
            query = query.options(*options)
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        *filters: ColumnElement[bool],
        order_by: Sequence[ColumnExpressionArgument] | None = None,
        limit: int = 100,
        offset: int = 0,
        options: list[ExecutableOption] | None = None,
        for_update: bool = False,
    ) -> list[T]:
        """
        Get list of model instances by filters.
        :param order_by: Optional list of expressions to order the results by.
        :param limit: Maximum number of rows to return.
        :param offset: Number of rows to skip before returning results.
        :param filters: List of model filters.
        :param options: Optional list of SQLAlchemy loader options
            (e.g. `selectinload`).
        :param for_update: Lock database rows for update.
        :return: Model instance. Raises EntityNotFoundError.
        """
        query = select(self.model_type).where(*filters).limit(limit).offset(offset)
        if order_by:
            query = query.order_by(*order_by)
        if options:
            query = query.options(*options)
        if for_update:
            query = query.with_for_update()
        return list((await self.session.scalars(query)).all())
