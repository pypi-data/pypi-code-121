import abc
from typing import Any, ClassVar, Generic, Iterable, Type, TypeVar, cast

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql.selectable import Select

from .base import GenericBaseRepository, _Create, _Id, _Item, _Replace, _Update
from .exceptions import ItemNotFoundException
from .mapper import Mapper

_Model = TypeVar("_Model")


class DatabaseRepository(
    Generic[_Model, _Create, _Update, _Replace, _Item, _Id],
    GenericBaseRepository[_Id, _Create, _Update, _Replace, _Item],
    abc.ABC,
):
    """Base SQLAlchemy-based cruds.

    Args:
        session (AsyncSession): The session to be used for queries.

    Variables:
        model_class (ClassVar[Type[Base]]): The mapper model class.
        primary_key (sa.Column): The primary key column.
    """

    model_class: ClassVar[Type[Any] | None] = None
    primary_key_column: ClassVar[sa.Column | None] = None

    def __init__(
        self,
        session: AsyncSession,
        item_mapper: Mapper[_Model, _Item],
        create_mapper: Mapper[_Create, _Model],
        update_mapper: Mapper[_Update, dict[str, Any]],
        replace_mapper: Mapper[_Replace, dict[str, Any]],
    ) -> None:
        """Initialize this crud instance.

        Args:
            session (AsyncSession): The SQLAlchemy async session to use.
            item_mapper (Mapper[_Model, _Item]): The mapper implementation to map
                models to items.
            create_mapper (Mapper[_Create, _Model]): Mapper to build item models.
            update_mapper (Mapper[_Update, dict[str,Any]]): Mapper between update
                payload and dict.
            replace_mapper (Mapper[_Replace, dict[str,Any]]): Mapper to replace an
                existing item.
        """

        assert session is not None
        self.session = session
        self.item_mapper = item_mapper
        self.create_mapper = create_mapper
        self.update_mapper = update_mapper
        self.replace_mapper = replace_mapper

    @classmethod
    def get_db_model(cls) -> Type[_Model]:
        """Retrieve the database model.

        Returns:
            ModelType: The model class to use.
        """
        assert cls.model_class is not None, (
            "The database model was not set for `{class_name}`. Please set the "
            "`{class_name}.model_class` attribute or override "
            "`{class_name}.{get_model_method}` method."
        ).format(
            get_model_method=cls.get_db_model.__name__,
            class_name=f"{cls.__module__}.{cls.__qualname__}",  # type: ignore
        )
        assert isinstance(cls.model_class, DeclarativeMeta)
        return cast(Type[_Model], cls.model_class)

    def get_base_query(self) -> Select:
        """Retrieve a base query.

        Returns:
            Select: The base query.
        """
        return sa.select(self.get_db_model())

    @classmethod
    def get_id_field(cls) -> sa.Column:
        """Retrieve the primary key column.

        Multi-column primary keys are not supported.

        Returns:
            sa.Column: The primery key column.
        """
        assert cls.primary_key_column is not None, (
            "The primary key column was not set. Please set the "
            "`{class_name}.primary_key_column` attribute or override the "
            "`{class_name}.{method_name}` method."
        ).format(
            class_name=f"{cls.__module__}.{cls.__name__}",  # type: ignore
            method_name=cls.get_id_field.__name__,
        )
        return cls.primary_key_column

    def decorate_query(self, select: Select, **query_filters: Any) -> Select:
        """Decorate the given query.

        Adds conditions, ordering and some other query stuff to the given query.

        Parameters:
            select: A base selectable object.

        Returns:
            Select: A modified query.
        """
        return select

    async def get_unmapped_by_id(self, id: _Id) -> _Model:
        result = await self.session.scalar(
            self._get_query().where(self.get_id_field() == id)
        )

        if result is None:
            raise ItemNotFoundException()

        return result

    def _get_query(self, **query_filters: Any) -> Select:
        return self.decorate_query(self.get_base_query(), **query_filters)

    def _get_list_query(
        self,
        offset: int = None,
        size: int = None,
        **query_filters: Any,
    ) -> Select:
        query = self._get_query(**query_filters)

        if size:
            query = query.limit(size)

        if offset:
            query = query.offset(offset)

        return query

    def map_item(self, session: Session, item: _Model) -> _Item:
        return self.item_mapper.map_item(item)

    def map_items(self, session: Session, items: Iterable[_Model]) -> list[_Item]:
        return [self.map_item(session, item) for item in items]

    async def get_by_id(self, id: _Id) -> _Item:
        return await self.session.run_sync(
            self.map_item, await self.get_unmapped_by_id(id)
        )

    async def get_count(self, **query_filters: Any) -> int:
        return await self.session.scalar(
            self.decorate_query(
                sa.select(sa.func.count(self.get_id_field())), **query_filters
            )
        )

    async def get_list(
        self, *, offset: int = None, size: int = None, **query_filters: Any
    ) -> list[_Item]:
        query = self._get_list_query(offset, size, **query_filters)

        return await self.session.run_sync(
            self.map_items, await self.session.scalars(query)
        )

    async def add(self, payload: _Create) -> _Item:
        model = self.create_mapper(payload)
        assert isinstance(model, self.get_db_model())

        async with self.session.begin_nested():
            await self.postprocess_model(model)
            self.session.add(model)

        return await self.session.run_sync(self.map_item, model)

    async def postprocess_model(self, model: _Model):
        pass

    async def remove(self, id: _Id):
        model = await self.get_unmapped_by_id(id)

        async with self.session.begin_nested():
            await self.session.delete(model)

    async def _update(self, id: _Id, payload: dict[str, Any]) -> _Item:
        model = await self.get_unmapped_by_id(id)

        async with self.session.begin_nested():
            self._patch_with(model, payload)

        return await self.session.run_sync(self.map_item, model)

    def _patch_with(self, model: _Model, payload: dict[str, Any]):
        for attr, value in payload.items():
            setattr(model, attr, value)

    async def update(self, id: _Id, payload: _Update) -> _Item:
        return await self._update(id, self.update_mapper(payload, exclude_unset=True))

    async def replace(self, id: _Id, payload: _Replace):
        return await self._update(id, self.replace_mapper(payload))
