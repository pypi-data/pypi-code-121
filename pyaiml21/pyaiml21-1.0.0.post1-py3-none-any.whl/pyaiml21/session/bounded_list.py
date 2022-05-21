"""Bounded list used as a history of a session."""
from typing import Optional, Any, List, TypeVar, Generic


ListItem = TypeVar("ListItem")


class BoundedList(Generic[ListItem]):
    """Represents a bounded list, a list with predefined max size."""

    def __init__(self, maxsize: Optional[int] = None):
        """
        Create a bounded list.

        :param maxsize: maximum size of bounded list, `None` for infinite list
        """
        assert maxsize is None or maxsize >= 0
        self.maxsize = maxsize
        """Maximal size of the list, or `None` for infinite list."""
        self._items: List[ListItem] = []
        self._list_start = 0  # 0 for infinite lists
        """idx where to put next item in full finite list"""

    @property
    def is_infinite(self) -> bool:
        """Return True if the list is infinite."""
        return self.maxsize is None

    @property
    def capacity(self) -> int:
        """Get the number of items currently in the list."""
        return len(self._items)

    def __getitem__(self, index: int) -> Optional[ListItem]:
        """
        Return the item at the given position.

        If no such item exists or is outside the list, return None.

        :param index: index of item to return, 0 denotes the newest item;
                      negative indexes denote counting from the oldest items
                      (-1 for the oldest)
        :return: item at the given index or None if no such item exists
        """
        assert isinstance(index, int)
        n_items = self.capacity
        if not (0 <= index < n_items or -n_items <= index < 0):
            return None
        idx = (self._list_start - index - 1) % self.capacity
        return self._items[idx]

    def add(self, item: Any) -> None:
        """
        Add new item to the list, possibly overwriting the oldest item.

        Place item into the list, if the capacity is more than maxsize
        and list is finite, overwrite the oldest item on the list.

        Implementation note: change if allowed removing

        :param item: item to place into the list
        """
        if self.maxsize == 0:
            return
        n_items = self.capacity
        if self.maxsize is None or n_items < self.maxsize:
            self._items.append(item)
        else:
            self._items[self._list_start] = item
            self._list_start = (self._list_start + 1) % self.maxsize
