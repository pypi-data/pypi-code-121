from __future__ import annotations

from typing import TYPE_CHECKING

from ._common import _JudyCommon
from .exceptions import JudyError
from .internal import _cjudy, _ffi, _load

if TYPE_CHECKING:
    from typing import Iterable, Tuple

    TKey = int

__all__ = ["JudyL", "JudyLIterator"]

_load()


class JudyLIterator:
    def __init__(self, j: JudyL) -> None:
        self._j = j
        self._array = j._array  # noqa
        self._start = True
        self._index = _ffi.new("signed long*")

    def __iter__(self):
        return self

    def __next__(self) -> tuple[int, int]:
        err = _ffi.new("JError_t *")
        if self._start:
            p = _cjudy.JudyLFirst(self._array[0], self._index, err)
            self._start = False
        else:
            p = _cjudy.JudyLNext(self._array[0], self._index, err)
        if p == _ffi.NULL:
            raise StopIteration()
        if p == JudyL.M1:
            raise JudyError(err.je_Errno)
        v = _ffi.cast("signed long", p[0])
        return self._index[0], int(v)


class JudyL(_JudyCommon):
    """
    JudyL class.
    """

    M1 = _ffi.cast("void*", -1)

    def __init__(self, other=None):
        self._array = _ffi.new("JudyL **")
        if other:
            self.update(other)

    def clear(self) -> None:
        err = _ffi.new("JError_t *")
        if _cjudy.JudyLFreeArray(self._array, err) == -1:
            raise JudyError(err.je_Errno)

    def __len__(self) -> int:
        err = _ffi.new("JError_t *")
        rc = _cjudy.JudyLCount(self._array[0], 0, -1, err)
        if rc == -1:
            raise JudyError(err.je_Errno)
        return rc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def __setitem__(self, key: int, value: int) -> None:
        err = _ffi.new("JError_t *")
        p = _cjudy.JudyLIns(self._array, key, err)
        if p == _ffi.NULL:
            raise JudyError(err.je_Errno)
        p[0] = _ffi.cast("void*", value)

    def __getitem__(self, item: int) -> int:
        err = _ffi.new("JError_t *")
        p = _cjudy.JudyLGet(self._array[0], item, err)
        if p == _ffi.NULL:
            raise KeyError(item)
        if p == JudyL.M1:
            raise JudyError(err.je_Errno)
        return int(_ffi.cast("signed long", p[0]))

    def __contains__(self, item: int) -> bool:
        err = _ffi.new("JError_t *")
        p = _cjudy.JudyLGet(self._array[0], item, err)
        if p == JudyL.M1:
            raise JudyError(err.je_Errno)
        return p != _ffi.NULL

    def get(self, item: int, default_value: int = 0) -> int:
        err = _ffi.new("JError_t *")
        p = _cjudy.JudyLGet(self._array[0], item, err)
        if p == _ffi.NULL:
            return default_value
        if p == JudyL.M1:
            raise JudyError(err.je_Errno)
        return int(_ffi.cast("signed long", p[0]))

    def inc(self, key: int, value: int = 1) -> None:
        err = _ffi.new("JError_t *")
        p = _cjudy.JudyLIns(self._array, key, err)
        if p == _ffi.NULL:
            raise JudyError(err.je_Errno)
        p[0] = int(_ffi.cast("signed long", p[0])) + _ffi.cast("void*", value)

    def __iter__(self):
        return JudyLIterator(self)

    def _start_iter(self):
        err = _ffi.new("JError_t *")
        index = _ffi.new("signed long*")
        p = _cjudy.JudyLFirst(self._array[0], index, err)
        if p == JudyL.M1:
            raise Exception(f"err={err.je_Errno}")
        return err, index, p

    def items(self) -> Iterable[tuple[int, int]]:
        err, index, p = self._start_iter()
        if p == _ffi.NULL:
            return
        v = int(_ffi.cast("signed long", p[0]))
        yield index[0], v
        while 1:
            p = _cjudy.JudyLNext(self._array[0], index, err)
            if p == JudyL.M1:
                raise Exception(f"err={err.je_Errno}")
            if p == _ffi.NULL:
                break
            v = int(_ffi.cast("signed long", p[0]))
            yield index[0], v

    def keys(self) -> Iterable[int]:
        err, index, p = self._start_iter()
        if p == _ffi.NULL:
            return
        yield index[0]
        while 1:
            p = _cjudy.JudyLNext(self._array[0], index, err)
            if p == JudyL.M1:
                raise Exception(f"err={err.je_Errno}")
            if p == _ffi.NULL:
                break
            yield index[0]
