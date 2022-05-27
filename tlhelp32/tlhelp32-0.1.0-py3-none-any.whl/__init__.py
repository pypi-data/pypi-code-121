"""
Tool Help Library
~~~~~~~~~~~~~~~~~

Traversing a snapshot:

    >>> import tlhelp32
    >>> with tlhelp32.Snapshot() as snapshot:
    >>>     [heap for heap in snapshot.heaps]
    >>>     [module for module in snapshot.modules]
    >>>     [process for process in snapshot.processes]
    >>>     [thread for heap in snapshot.threads]
    [Heap(pid=..., id_=...), Heap(pid=..., id_=...), ...]
    [Module(base_addr=..., size=..., handle=..., name=..., path=...), ...]
    [Process(pid=..., num_threads=..., parent=..., priority=..., name=...), ...]
    [Thread(id_=..., owner=..., priority=...), ...]
"""  # noqa

from __future__ import annotations

import ctypes

from ._ctypes import Toolhelp32ReadProcessMemory
from .errors import AllocationError, SecurityError
from .heap import HeapListSnapshot
from .module import ModuleSnapshot
from .process import ProcessSnapshot
from .snapshot import Snapshot
from .thread import ThreadSnapshot

__all__ = [
    "Snapshot",
    "HeapListSnapshot",
    "ModuleSnapshot",
    "ProcessSnapshot",
    "ThreadSnapshot",
    "read_process_memory",
]


def read_process_memory(
    base: int, nbytes: int, pid: int = 0, raise_unequal: bool = False
) -> bytes:
    """Returns a memory segment of a specified size for a process.

    Use the Win32 `ReadProcessMemory` function instead if you plan to perform
    several reads. Use `GetProcessMemoryInfo` function to get information
    related to the memory usage of a process.

    Args:
        base (int): Base address of the process to read the memeory from.
        nbytes (int): Number of bytes to read from `base`.
        pid (int, optional): PID of the process. Defaults to 0. If it is 0,
            memory from the current / calling process is read.
        raise_unequal (bool, optional): Raise an exception if the size of the
            buffer filled by the system doesn't equal `nbytes`. Defaults to
            False.

    Returns:
        bytes: Process memory of size `nbytes` (if everything went well).

    Raises:
        AllocationError: If `raise_unequal` is True and the size of the return
            object doesn't equal `nbytes`.
        SecurityError: If the entire area of memory pointed to by `base` till
            `nbytes` is not accessible for reading.
    """
    buf = ctypes.create_string_buffer(nbytes)
    if Toolhelp32ReadProcessMemory(pid, base, buf, nbytes, None) != 1:  # TRUE
        raise SecurityError
    ret = bytes(buf)
    if len(ret) != nbytes and raise_unequal:
        raise AllocationError
    return ret
