"""Exposes the module snapshot functionality."""

from __future__ import annotations

import dataclasses
import pathlib

from ._base import BaseIterator, BaseSnapshot, DataclassMixin, Snap, struct_member
from ._ctypes import MODULEENTRY32W, Module32FirstW, Module32NextW

__all__ = ["Module", "ModuleSnapshot"]


@dataclasses.dataclass
class Module(DataclassMixin):
    """Describes a module belonging to a particular process."""

    base_addr: int = struct_member("modBaseAddr")
    """Base address of the module in the context of the owning process."""

    size: int = struct_member("modBaseSize")
    """File size of the module (in bytes)."""

    handle: int = struct_member("hModule")
    """Memory address of the module in the context of the owning process."""

    name: str = struct_member("szModule")
    """File name of the module e.g. "python.exe"."""

    path: pathlib.Path = struct_member("szExePath")
    """Full file path to the module. e.g. "C:/Python3.10/python310.dll"."""

    def __post_init__(self):
        if self.base_addr:
            self.base_addr = int.from_bytes(self.base_addr, "little")
        if self.path:
            self.path = pathlib.Path(self.path)


class ModuleIterator(BaseIterator):
    _first_fn = Module32FirstW
    _next_fn = Module32NextW
    _dt_type = Module


class ModuleSnapshot(BaseSnapshot):
    """Enumerates the modules belonging to a particular process."""

    def __init__(self, pid: int = 0, include_32bit: bool = False) -> None:
        """Create a module snapshot.

        Args:
            pid (int, optional): The PID of the process whose modules are to
                be enumerated. Defaults to 0. If it is 0, then the modules for
                the current/calling process are enumerated.
            include_32bit (bool, optional): Enumerate 32-bit modules also.
                Valid only for 64-bit processes, else this parameter is
                ignored. Defaults to False.

        Raises:
            CreationFailedError: If the call fails internally.
        """
        snap_type = Snap.MODULE
        if include_32bit:
            snap_type |= Snap.MODULE32
        super().__init__(snap_type, pid)
        self._me = MODULEENTRY32W()

    def __iter__(self) -> ModuleIterator | None:
        return ModuleIterator(self._handle, self._me)
