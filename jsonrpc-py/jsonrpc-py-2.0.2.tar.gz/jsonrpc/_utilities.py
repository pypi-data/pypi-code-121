# Pure zero-dependency JSON-RPC 2.0 implementation.
# Copyright © 2022 Andrew Malchuk. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Callable, Hashable, Iterable, Iterator, MutableMapping
from itertools import filterfalse, tee
from time import gmtime
from typing import Any, Final, Literal, TypeVar

__all__: Final[list[str]] = [
    "http_rfc2822_datetime",
    "make_hashable",
    "partition",
    "Undefined",
    "UndefinedType"
]

_T = TypeVar("_T")


def http_rfc2822_datetime(timestamp: float | None = None) -> str:
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, _, _ = gmtime(timestamp)
    return f"{['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][tm_wday]}, {tm_mday:02d} " \
        f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][tm_mon - 1]} " \
        f"{tm_year:04d} {tm_hour:02d}:{tm_min:02d}:{tm_sec:02d} GMT"


def make_hashable(obj: Any, /) -> Hashable:
    if isinstance(obj, MutableMapping):
        return tuple((key, make_hashable(value)) for key, value in sorted(obj.items()))

    # Try hash to avoid converting a hashable iterable (e.g. string, frozenset)
    # to a tuple:
    try:
        hash(obj)
    except TypeError:
        if isinstance(obj, Iterable):
            return tuple(map(make_hashable, obj))
        # Non-hashable, non-iterable:
        raise

    return obj


def partition(predicate: Callable[[_T], bool] | None, iterable: Iterable[_T], /) -> Iterator[_T]:
    # Use a predicate to partition entries into true entries and false entries.
    left, right = tee(iterable)
    yield from filter(predicate, left)
    yield from filterfalse(predicate, right)


class UndefinedType:
    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> Literal["Undefined"]:
        return "Undefined"

    def __hash__(self) -> Literal[0xDEADBEEF]:
        return 0xDEADBEEF

    def __eq__(self, obj: Any, /) -> bool:
        return isinstance(obj, self.__class__)

    def __bool__(self) -> Literal[False]:
        return False


Undefined: Final[UndefinedType] = UndefinedType()
