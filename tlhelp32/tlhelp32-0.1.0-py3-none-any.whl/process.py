"""Exposes the process snapshot functionality."""

from __future__ import annotations

import dataclasses

from ._base import BaseIterator, BaseSnapshot, DataclassMixin, Snap, struct_member
from ._ctypes import PROCESSENTRY32W, Process32FirstW, Process32NextW

__all__ = ["Process", "ProcessSnapshot"]


@dataclasses.dataclass
class Process(DataclassMixin):
    """Describes a process residing in the system address space."""

    pid: int = struct_member("th32ProcessID")
    """Process identifier."""

    num_threads: int = struct_member("cntThreads")
    """Number of execution threads started by the process."""

    parent: int = struct_member("th32ParentProcessID")
    """Identifier of the process that created this process."""

    priority: int = struct_member("pcPriClassBase")
    """base priority of any threads created by this process."""

    name: str = struct_member("szExeFile")
    """Name of the executable file for the process. e.g. "python3.exe"."""


class ProcessIterator(BaseIterator):
    _first_fn = Process32FirstW
    _next_fn = Process32NextW
    _dt_type = Process


class ProcessSnapshot(BaseSnapshot):
    """Enumerates all the processes residing in the system address space."""

    def __init__(self) -> None:
        """Create a process snapshot.

        Raises:
            CreationFailedError: If the call fails internally.
        """
        super().__init__(Snap.PROCESS)
        self._pe = PROCESSENTRY32W()

    def __iter__(self) -> ProcessIterator | None:
        return ProcessIterator(self._handle, self._pe)
