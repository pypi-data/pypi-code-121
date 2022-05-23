import typing

from .base import GenericBaseRepository, _Create, _Id, _Item, _Replace, _Update
from .mapper import Mapper

_Repo = typing.TypeVar("_Repo", bound=GenericBaseRepository)
_MappedItem = typing.TypeVar("_MappedItem")
_MappedCreate = typing.TypeVar("_MappedCreate")
_MappedUpdate = typing.TypeVar("_MappedUpdate")
_MappedReplace = typing.TypeVar("_MappedReplace")
_MappedId = typing.TypeVar("_MappedId")


class MappedRepository(
    GenericBaseRepository[
        _MappedId, _MappedCreate, _MappedUpdate, _MappedReplace, _MappedItem
    ],
    typing.Generic[
        _MappedId,
        _MappedCreate,
        _MappedUpdate,
        _MappedReplace,
        _MappedItem,
        _Id,
        _Create,
        _Update,
        _Replace,
        _Item,
    ],
):
    """Mapped data for repositories.

    This implements the repository interface by leveraging mappers between payloads,
    item and id for an underlying repository implementation.
    """

    def __init__(
        self,
        repository: GenericBaseRepository[_Id, _Create, _Update, _Replace, _Item],
        *,
        id_mapper: Mapper[_MappedId, _Id],
        create_mapper: Mapper[_MappedCreate, _Create],
        update_mapper: Mapper[_MappedUpdate, _Update],
        replace_mapper: Mapper[_MappedReplace, _Replace],
        item_mapper: Mapper[_Item, _MappedItem],
    ) -> None:
        """
        Initialize the `MappedRepository` instance.

        Args:
            id_mapper: A mapper to transform the item ID.
            create_mapper: A mapper to add new items.
            update_mapper: Mapper to update an item.
            replace_mapper: Maps the replace payload.
            item_mapper: The item mapper from the repository implementation.
            repository: The underlying repository implementations.
        """
        super().__init__()
        self.repository = repository
        self.item_mapper = item_mapper
        self.id_mapper = id_mapper
        self.create_mapper = create_mapper
        self.update_mapper = update_mapper
        self.replace_mapper = replace_mapper

    async def add(self, payload: _MappedCreate) -> _MappedItem:
        return self.item_mapper(await self.repository.add(self.create_mapper(payload)))

    async def update(self, id: _MappedId, payload: _MappedUpdate) -> _MappedItem:
        return self.item_mapper(
            await self.repository.update(
                self.id_mapper(id), self.update_mapper(payload)
            )
        )

    async def get_by_id(self, id: _MappedId) -> _MappedItem:
        return self.item_mapper(await self.repository.get_by_id(self.id_mapper(id)))

    async def replace(self, id: _MappedId, payload: _MappedReplace) -> _MappedItem:
        return self.item_mapper(
            await self.repository.replace(
                self.id_mapper(id), self.replace_mapper(payload)
            )
        )

    async def get_count(self, **query_filters: typing.Any) -> int:
        return await self.repository.get_count(**query_filters)

    async def get_list(
        self,
        *,
        offset: typing.Optional[int] = None,
        size: typing.Optional[int] = None,
        **query_filters: typing.Any,
    ) -> list[_MappedItem]:
        return [
            self.item_mapper(item)
            for item in await self.repository.get_list(
                offset=offset, size=size, **query_filters
            )
        ]

    async def remove(self, id: _MappedId):
        return await self.repository.remove(self.id_mapper(id))
