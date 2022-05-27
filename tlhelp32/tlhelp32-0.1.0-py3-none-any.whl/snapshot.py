"""AIO snapshot - This is what you will need most of the times.

As compared to taking 4 different snapshots, this module provides a class
which does it at once. Also 4 different snapshots means they get taken at
different times capturing a different state of the system (even if its just a
matter of seconds).
"""

from ._base import BaseSnapshot, Snap
from ._ctypes import (
    HEAPENTRY32,
    HEAPLIST32,
    MODULEENTRY32W,
    PROCESSENTRY32W,
    THREADENTRY32,
)
from .heap import HeapIterator
from .module import ModuleIterator
from .process import ProcessIterator
from .thread import ThreadIterator

__all__ = ["Snapshot"]


class Snapshot(BaseSnapshot):
    """All-in-one snapshot."""

    def __init__(self, pid: int = 0, include_32bit: bool = False) -> None:
        """Create a snapshot containing the heaps, modules, processes and threads.

        Args:
            pid (int, optional): The PID of the process whose modules and heaps
                are to be enumerated. Defaults to 0. If it is 0, then the
                enumeration takes place for the current / calling process.
            include_32bit (bool, optional): Passed to `ModuleSnapshot`.

        Raises:
            CreationFailedError: If the call fails internally.
        """
        snap_type = Snap.ALL
        if include_32bit:
            snap_type |= Snap.MODULE32
        super().__init__(snap_type, pid)
        self._pid = pid
        self._he = HEAPENTRY32()
        self._hl = HEAPLIST32()
        self._me = MODULEENTRY32W()
        self._pe = PROCESSENTRY32W()
        self._te = THREADENTRY32()

    @property
    def heaps(self) -> HeapIterator:
        """Iterator for the heaps present in the snapshot."""
        return HeapIterator(self._handle, self._hl)

    @property
    def modules(self) -> ModuleIterator:
        """Iterator for the modules present in the snapshot."""
        return ModuleIterator(self._handle, self._me)

    @property
    def processes(self) -> ProcessIterator:
        """Iterator for the processes present in the snapshot."""
        return ProcessIterator(self._handle, self._pe)

    @property
    def threads(self) -> ThreadIterator:
        """Iterator for the threads present in the snapshot."""
        return ThreadIterator(self._handle, self._te)
