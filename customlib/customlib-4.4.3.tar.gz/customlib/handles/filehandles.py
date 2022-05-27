# -*- coding: UTF-8 -*-

from os import fsync
from typing import IO

from .core import AbstractHandle
from .lockhandle import FileLock
from ..constants import RECURSIVE_THREAD_LOCK


class FileHandle(AbstractHandle):
    """Simple handle with thread lock and file lock management."""

    def __init__(self, *args, **kwargs):
        super(FileHandle, self).__init__(*args, **kwargs)
        self._file_lock = FileLock()

    @staticmethod
    def new(*args, **kwargs):
        """Returns a new file handle."""
        return open(*args, **kwargs)

    def acquire(self, *args, **kwargs):
        """Returns a new locked file handle."""
        with RECURSIVE_THREAD_LOCK:
            handle = self.new(*args, **kwargs)
            self._lock(handle)
            return handle

    def release(self, handle: IO):
        """Close the file handle and release the resources."""
        with RECURSIVE_THREAD_LOCK:
            handle.flush()
            if "r" not in handle.mode:
                fsync(handle.fileno())
            self._unlock(handle)
            handle.close()

    def _lock(self, handle: IO, flags: int = None):
        """Acquire a lock on the file handle."""
        if flags is None:
            flags = self._file_lock.get_flags(handle)
        self._file_lock.lock(handle, flags)

    def _unlock(self, handle: IO):
        """Unlock the file handle before closing it."""
        self._file_lock.unlock(handle)
