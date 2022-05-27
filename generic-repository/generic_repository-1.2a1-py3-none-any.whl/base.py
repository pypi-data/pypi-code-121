import abc
from typing import Any, Generic, Optional, TypeVar

_Create = TypeVar("_Create")
_Update = TypeVar("_Update")
_Replace = TypeVar("_Replace")
_Item = TypeVar("_Item")
_Id = TypeVar("_Id")


class GenericBaseRepository(
    Generic[_Id, _Create, _Update, _Replace, _Item],
    abc.ABC,
):  # pragma nocover
    """Base class for all CRUD implementations."""

    @abc.abstractmethod
    async def get_by_id(self, id: _Id, **kwargs: Any) -> _Item:
        """Retrieve an item by it's ID.

        Args:
            id: The item ID to retrieve.

        Returns:
            _Item: The item.

        Raises:
            ItemNotFoundError: If the item cannot be found.
        """
        raise NotImplementedError()

    async def get_count(self, **query_filters: Any) -> int:
        """Retrieve a total count of items.

        Returns:
            int: _description_
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_list(
        self,
        *,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        **query_filters: Any
    ) -> list[_Item]:
        """Retrieve a list of items.

        Args:
            offset: Where to start retrieving items.. Defaults to None.
            size: How many items to retrieve.. Defaults to None.

        Returns:
            list[_Item]: A list containing the items found.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def add(self, payload: _Create, **kwargs: Any) -> _Item:
        """Add a new item.

        Args:
            payload: The data to use when adding the new item.

        Raises:
            InvalidPayloadException: If the payload is not valid.

        Returns:
            _Item: The newly created item.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def remove(self, id: _Id, **kwargs: Any):
        """Remove the item identified by the supplied ID.

        Args:
            id: The item ID to remove.

        Raises:
            ItemNotFoundException: If the item does not exist.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: _Id, payload: _Update, **kwargs: Any) -> _Item:
        """Update an item.

        Args:
            id: The item ID to update.
            payload: The new data to apply to the item.

        Returns:
            _Item: The updated item.

        Raises:
            ItemNotFoundError: If the item cannot be found.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def replace(self, id: _Id, payload: _Replace, **kwargs: Any) -> _Item:
        """Replace an item in the store.

        Args:
            id: The item ID to update.
            payload: The new data to apply to the item.

        Returns:
            _Item: The updated item.

        Raises:
            ItemNotFoundError: If the item cannot be found.
        """
        raise NotImplementedError()
