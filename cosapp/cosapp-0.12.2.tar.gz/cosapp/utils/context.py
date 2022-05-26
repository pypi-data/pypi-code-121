from typing import Any


class ContextLock:
    """Simple locker to track an execution task is going on."""

    def __init__(self):
        self.__locked = False

    def __enter__(self):
        self.__locked = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.__locked = False

    def is_locked(self) -> bool:
        """Is the context lock locked?"""
        return self.__locked
