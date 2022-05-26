from __future__ import annotations

from queue import Queue
from typing import Iterator, TypeVar, Union

T = TypeVar("T")


class Stream(Iterator[T]):
    """Wraps a Queue and iterates over its values"""

    __queue: Queue[Union[T, StopIteration]]
    __cancelled: bool
    is_alive: bool

    def __init__(self):
        self.__queue = Queue()
        self.__cancelled = False

    @classmethod
    def from_queue(cls, queue: Queue[T]):
        q = cls()
        q.__queue = queue
        return q

    @property
    def is_alive(self) -> bool:
        return not self.__cancelled

    def put(self, item: T) -> None:
        if not self.is_alive:
            raise RuntimeError("Cannot add item to cancelled stream")
        self.__queue.put(item)

    def cancel(self) -> None:
        if not self.is_alive:
            raise RuntimeError("Stream was already cancelled")
        self.__queue.put(StopIteration())
        self.__cancelled = True

    def __next__(self) -> T:
        item = self.__queue.get()
        if isinstance(item, StopIteration):
            self.__cancelled = True
            raise item
        return item

    def __iter__(self):
        return self
