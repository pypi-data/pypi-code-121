"""Exposes the thread snapshot functionality."""

from __future__ import annotations

import dataclasses

from ._base import BaseIterator, BaseSnapshot, DataclassMixin, Snap, struct_member
from ._ctypes import THREADENTRY32, Thread32First, Thread32Next


@dataclasses.dataclass
class Thread(DataclassMixin):
    """Describes a thread executing on the system."""

    id_: int | None = struct_member("th32ThreadID")
    """The thread identifier.

    Compatible with the thread identifier returned by the CreateProcess
    function."""

    owner: int | None = struct_member("th32OwnerProcessID")
    """The identifier of the process that created the thread."""

    priority: int | None = struct_member("tpBasePri")
    """The kernel base priority level assigned to the thread.

    The priority is a number from 0 to 31, with 0 representing the lowest
    possible thread priority."""


class ThreadIterator(BaseIterator):
    """Iterator returned by `ThreadSnapshot`."""

    _first_fn = Thread32First
    _next_fn = Thread32Next
    _dt_type = Thread


class ThreadSnapshot(BaseSnapshot):
    """Enumerates all the threads executing on the system."""

    def __init__(self) -> None:
        """Create a thread snapshot.

        Raises:
            CreationFailedError: If the call fails internally.
        """
        super().__init__(Snap.THREAD)
        self._te = THREADENTRY32()

    def __iter__(self) -> ThreadIterator | None:
        return ThreadIterator(self._handle, self._te)
