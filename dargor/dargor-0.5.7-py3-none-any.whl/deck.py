#
# Copyright (c) 2022, Gabriel Linder <linder.gabriel@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

from contextlib import suppress
from itertools import islice
from typing import (
    Deque,
    MutableSequence,
    SupportsIndex,
    TypeVar,
    Union,
    overload,
)

T = TypeVar('T')


class deck(Deque[T]):

    @overload
    def __getitem__(self, val: SupportsIndex) -> T:  # noqa: U100
        ...

    @overload
    def __getitem__(self, val: slice) -> MutableSequence[T]:  # noqa: U100
        ...

    def __getitem__(self, val: Union[SupportsIndex, slice]) -> Union[
            T, MutableSequence[T]]:

        if type(val) is slice:

            with suppress(TypeError):
                if val.start < 0:
                    start = max(val.start + len(self), 0)
                    val = slice(start, val.stop, val.step)
            assert val.start is None or val.start >= 0, val.start

            with suppress(TypeError):
                if val.stop < 0:
                    stop = max(val.stop + len(self), 0)
                    val = slice(val.start, stop, val.step)
            assert val.stop is None or val.stop >= 0, val.stop

            return list(islice(self, val.start, val.stop, val.step))

        return super().__getitem__(val)
