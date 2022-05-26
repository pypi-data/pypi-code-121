from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator, List, Tuple, TypeVar

ItemType = TypeVar("ItemType")


class Subscription(Iterator[ItemType], ABC):
    """Subscription to a stream of items provided by a SiLA Server"""

    def __init__(self):
        self.__callbacks: List[Callable[[ItemType], Any]] = []

    def add_callback(self, func: Callable[[ItemType], Any]) -> None:
        """
        Add a function to be called on every value update.
        Can only be used while this subscription is not cancelled.

        Parameters
        ----------
        func
            Function to be called on every value update.
            It will be called with the new value as positional parameter: ``func(new_value)``

        Raises
        ------
        RuntimeError
            If this subscription was cancelled

        Notes
        -----
        Can be used as a context manager:

        .. code-block:: python

            with thing.subscribe() as subscription:
                  do_something(subscription)
            # subscription is cancelled here

        """
        if self.is_cancelled:
            raise RuntimeError("Cannot add callbacks to cancelled streams")
        self.__callbacks.append(func)

    def clear_callbacks(self) -> None:
        """Deregister all currently registered callback functions"""
        self.__callbacks.clear()

    @property
    def callbacks(self) -> Tuple[Callable[[ItemType], Any], ...]:
        """All currently registered callback functions"""
        return tuple(self.__callbacks)

    @abstractmethod
    def cancel(self) -> None:
        """Cancel this subscription"""
        pass

    @property
    @abstractmethod
    def is_cancelled(self) -> bool:
        """``True`` is this subscription was cancelled"""
        pass

    def __enter__(self) -> Subscription[ItemType]:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.is_cancelled:
            self.cancel()
