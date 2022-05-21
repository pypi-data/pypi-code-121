from abc import abstractmethod
from typing import Callable


class StopwatchABS:
    def __init__(self, callback: Callable[[int], None] = ..., *args, **kwargs):
        """"""

    @abstractmethod
    def __enter__(self):
        """Reset timer before enter context manager."""

    @abstractmethod
    def __exit__(self, type, value, traceback) -> bool:
        """Call callback before exit context manager.
        
        The callback will receive:
            - Extra arguments from initialization
            - Context manager duration
            - Extra keyword arguments from initialization
        """

    @abstractmethod
    def __call__(self, func: Callable) -> Callable:
        """Time a function or method.
        
        The callback will receive:
            - Arguments from function
            - Extra arguments from initialization
            - Decorated function duration
            - Keyword arguments from function
            - Extra keyword arguments from initialization
        
        Note: Extra keyword arguments from initialization can
        overwrite the function keyword arguments.

        Note 2: The intention is to be easy to use with print() function,
        that's why duration is giving as argument and not keyword argument.
        """

    @abstractmethod
    async def __aenter__(self):
        """Reset timer before enter async context manager."""

    @abstractmethod
    async def __aexit__(self, type, value, traceback) -> bool:
        """Await callback before exit context manager.
        
        The callback will receive:
            - Extra arguments from initialization
            - Context manager duration
            - Extra keyword arguments from initialization
        """

    @abstractmethod
    def __str__(self) -> str:
        """Get the current timing as string."""

    @abstractmethod
    def __repr__(self) -> str:
        """Get the current timing as string."""

    @abstractmethod
    def reset(self):
        """Restart the timer."""

    @abstractmethod
    def get_record(self, name: int | str) -> int | None:
        """Get a record by name.

        Return None if no item is found.
        """

    @abstractmethod
    def get_records(self) -> dict[int | str, int]:
        """Get a dictionary with all records."""

    @abstractmethod
    def duration(self) -> int:
        """Get the elapsed time since start (or reset)."""

    @abstractmethod
    def record(self, name: str = ...):
        """Record current time.

        If a name is giving it'll use it as key, otherwise
        the quantity of nameless records will be used as key.
        """
