"""Exposes the heap snapshot functionality."""

from __future__ import annotations

import ctypes
import dataclasses
import enum
from ctypes import wintypes
from typing import ClassVar

from ._base import BaseIterator, BaseSnapshot, DataclassMixin, Snap, struct_member
from ._ctypes import (
    ERROR_NO_MORE_FILES,
    HEAPENTRY32,
    HEAPLIST32,
    Heap32First,
    Heap32ListFirst,
    Heap32ListNext,
    Heap32Next,
)

__all__ = ["HeapBlockKind", "HeapBlock", "Heap", "HeapListSnapshot"]


class HeapBlockKind(enum.IntEnum):  # noqa
    FIXED = 1
    """Block has a fixed (unmovable) location."""

    FREE = 2
    """Block is not used."""

    MOVEABLE = 4
    """Block location can be moved."""


@dataclasses.dataclass
class HeapBlock(DataclassMixin):
    """Describes one entry (block) of a heap that is being examined."""

    handle: int = struct_member("hHandle")
    """Underlying handle to the heap block."""

    start_addr: int = struct_member("dwAddress")
    """The linear address of the start of the block."""

    size: int = struct_member("dwBlockSize")
    """Size of the block (in bytes)."""

    kind: HeapBlockKind = struct_member("dwFlags")
    """Memory position characteristics of the block."""

    pid: int = struct_member("th32ProcessID")
    """The identifier of the process that uses the heap."""

    heap_id: int = struct_member("th32HeapID")
    """The heap identifier; it is not / doesn't point to a handle."""

    def __post_init__(self):
        self.kind = HeapBlockKind(self.kind)
        self.start_addr = int.from_bytes(self.start_addr, "little")
        self.heap_id = int.from_bytes(self.heap_id, "little")


@dataclasses.dataclass
class Heap(DataclassMixin):
    """Describes an entry from a list that enumerates the heaps used by a process."""

    _first: ClassVar[HEAPENTRY32]
    pid: int | None = struct_member("th32ProcessID")
    """The identifier of the process to be examined."""

    id_: int | None = struct_member("th32HeapID")
    """The heap identifier; it is not a handle."""

    def __post_init__(self):
        self._id_raw = self.id_
        self.id_ = int.from_bytes(self._id_raw, "little")

    def __iter__(self) -> HeapBlockIterator:
        return HeapBlockIterator(self._first, self.pid, self._id_raw)


class HeapBlockIterator(BaseIterator):
    _first_fn = Heap32First
    _next_fn = Heap32Next
    _dt_type = HeapBlock

    def __init__(self, first_heapentry, pid, heap_id):
        super().__init__(None, first_heapentry)
        self._pid = pid
        self._heap_id = heap_id

    def __next__(self) -> HeapBlock | None:
        """Returns the next heap block in the heap."""
        if self._first:
            if not self._first_fn(
                ctypes.byref(self._initial), self._pid, self._heap_id
            ):
                raise RuntimeError
            self._first = False
            return self._build_dataclass()
        if not self._next_fn(ctypes.byref(self._initial)):
            if ctypes.get_last_error() == ERROR_NO_MORE_FILES:
                raise StopIteration
            raise RuntimeError
        return self._build_dataclass()


class HeapIterator(BaseIterator):
    _first_fn = Heap32ListFirst
    _next_fn = Heap32ListNext
    _dt_type = Heap

    def __init__(self, handle: wintypes.HANDLE, first_heaplist: HEAPLIST32) -> None:
        super().__init__(handle, first_heaplist)
        Heap._first = self._he = HEAPENTRY32()


class HeapListSnapshot(BaseSnapshot):
    """Enumerates the heaps used by a particular process.

    Enumerating (a.k.a. walking) the heap is an expensive operation, look for
    ways to avoid redoing it or use the Win32 `HeapWalk` function instead for
    a much better performance.
    """

    def __init__(self, pid: int = 0) -> None:
        """Create a module snapshot.

        Args:
            pid (int, optional): The PID of the process whose modules are to
                be enumerated. Defaults to 0. If it is 0, then the modules for
                the current/calling process are enumerated.

        Raises:
            CreationFailedError: If the call fails internally.
        """
        super().__init__(Snap.HEAPLIST, pid)
        self._hl = HEAPLIST32()

    def __iter__(self) -> HeapIterator:
        return HeapIterator(self._handle, self._hl)
