"""Abstracts the underlying C API into a more Pythonic form."""

from __future__ import annotations

import abc
import ctypes
import dataclasses
import enum
from ctypes import wintypes as wt
from typing import Any, Callable, Type

from typing_extensions import Self

from ._ctypes import (
    ERROR_NO_MORE_FILES,
    INVALID_HANDLE_VALUE,
    TH32CS_INHERIT,
    TH32CS_SNAPALL,
    TH32CS_SNAPHEAPLIST,
    TH32CS_SNAPMODULE,
    TH32CS_SNAPMODULE32,
    TH32CS_SNAPPROCESS,
    TH32CS_SNAPTHREAD,
    CloseHandle,
    CreateToolhelp32Snapshot,
    SizedStructure,
)
from .errors import CreationFailedError


class Snap(enum.IntFlag):
    """Values used by the underlying function to denote the type of a snapshot."""

    INHERIT = TH32CS_INHERIT
    HEAPLIST = TH32CS_SNAPHEAPLIST
    MODULE = TH32CS_SNAPMODULE
    MODULE32 = TH32CS_SNAPMODULE32
    PROCESS = TH32CS_SNAPPROCESS
    THREAD = TH32CS_SNAPTHREAD
    ALL = TH32CS_SNAPALL


def struct_member(member: str, **kwargs) -> Any:
    """Extra metadata for the fields used by a dataclass.

    Args:
        member (str): The name of the corresponding member in the underlying
            structure.
    """
    return dataclasses.field(default=None, metadata={"member": member}, **kwargs)


class DataclassMixin(abc.ABC):
    """Provides an additional method for all dataclasses."""

    @classmethod
    def build(cls, ss: SizedStructure) -> Self:
        """Creates an instance from the valid members of the `SizedStructure`.

        How this works:
        1.  `SizedStructure.dwSize` is updated with the length of the structure
            each time it is passed to a function.
        2.  Any members of the struct whose offset is greater than this length
            are not to be used and might contain garbage values.
        """
        args = []
        expected = 0
        for name, type_ in ss._fields_:
            expected += ctypes.sizeof(type_)
            for field in dataclasses.fields(cls):
                member = field.metadata["member"]
                if member == name and ss.dwSize >= expected:
                    args.append(getattr(ss, member))
        return cls(*args)


class BaseSnapshot(abc.ABC):
    """Base class for all `*Snapshot` classes."""

    def __init__(self, type_: Snap, pid: int = 0) -> None:  # noqa
        self._type = type_
        self._pid = pid
        ptr = CreateToolhelp32Snapshot(type_, pid)
        if ptr == INVALID_HANDLE_VALUE:
            raise CreationFailedError
        self._handle = ptr

    def __enter__(self, *_) -> Self:
        return self

    def __repr__(self) -> str:
        return f"<Snapshot type={self._type}, pid={self._pid}>"

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> bool:
        """Close the underlying snapshot handle and free up resources.

        Returns:
            bool: Whether the underlying handle was closed successfully.
        """
        if self._handle:  # pragma: no cover
            return bool(CloseHandle(self._handle))
        return False


class BaseIterator(abc.ABC):
    """Base iterator class for all `*Iterator` classes."""

    _first_fn: Callable[[wt.HANDLE, ctypes.pointer[SizedStructure]], wt.BOOL]
    """Retrieves the first element from an iterator, akin to `iter()`."""

    _next_fn: Callable[[wt.HANDLE, ctypes.pointer[SizedStructure]], wt.BOOL]
    """Retrives the next element from an iterator every time until the end."""

    _dt_type: Type[DataclassMixin]
    """The type of dataclass returned by this iterator."""

    def __init__(self, handle: wt.HANDLE, first_struct: SizedStructure) -> None:
        """Create an iterator wrapping `_first_fn` and `_next_fn`.

        Args:
            handle (wt.HANDLE): Handle to the snapshot.
            first_struct (SizedStructure): Handle to the first instance of the
                underlying structure.
        """
        self._first = True
        self._handle = handle
        self._initial = first_struct

    def _build_dataclass(self) -> _dt_type:
        d = self._dt_type.build(self._initial)
        self._initial.reset_size()
        return d

    def __next__(self) -> _dt_type:
        if self._first:
            if not self._first_fn(
                self._handle, ctypes.byref(self._initial)
            ):  # pragma: no cover
                raise RuntimeError
            self._first = False
            return self._build_dataclass()
        if not self._next_fn(
            self._handle, ctypes.byref(self._initial)
        ):  # pragma: no cover
            if ctypes.get_last_error() == ERROR_NO_MORE_FILES:
                raise StopIteration
            raise RuntimeError
        return self._build_dataclass()

    def __iter__(self) -> Self:
        return self
