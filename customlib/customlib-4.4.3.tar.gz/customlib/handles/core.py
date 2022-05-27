# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod

from ..constants import RECURSIVE_THREAD_LOCK


class AbstractHandle(ABC):
    """Base abstract handle for all context-manager classes in this module."""

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs

    def __enter__(self):
        RECURSIVE_THREAD_LOCK.acquire()
        if hasattr(self, "_handle") is False:
            self._handle = self.acquire(*self._args, **self._kwargs)
        return self._handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "_handle") is True:
            self.release(self._handle)
            del self._handle
        RECURSIVE_THREAD_LOCK.release()

    @abstractmethod
    def acquire(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def release(self, *args, **kwargs):
        raise NotImplementedError
