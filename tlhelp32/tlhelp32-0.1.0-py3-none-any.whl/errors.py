"""Exceptions used by tlhelp32."""

import abc
import ctypes

__all__ = ["AllocationError", "CreationFailedError", "SecurityError"]


class Error(abc.ABC, WindowsError):
    """Base exception class used by tlhelp32."""

    def __init__(self):
        super().__init__()
        self._gle = ctypes.get_last_error()

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {__doc__}"

    __str__ = __repr__


class AllocationError(Error):
    """Requested amount of memory couldn't be copied."""


class CreationFailedError(Error):
    """Snapshot couldn't be created due to an internal error or an invalid PID."""

    def __repr__(self) -> str:
        cls = type(self).__name__
        gle = self._gle
        msg = ctypes.FormatError(gle)
        return f"{cls}: Snapshot creation failed with error {gle} [{msg}]"


class SecurityError(Error):
    """Specified process doesn't allow read access to its memory."""
