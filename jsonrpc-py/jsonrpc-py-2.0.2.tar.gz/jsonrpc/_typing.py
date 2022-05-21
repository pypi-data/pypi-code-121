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

from collections.abc import Iterable, Iterator, MutableMapping, MutableSequence
from types import TracebackType
from typing import Any, Final, Protocol, TypeAlias

__all__: Final[list[str]] = [
    "ExcInfo",
    "Headers",
    "InputStream",
    "StartResponse",
    "WSGIEnvironment"
]

Headers: TypeAlias = MutableSequence[tuple[str, str]]
ExcInfo: TypeAlias = tuple[type[Exception], Exception, TracebackType | None]
WSGIEnvironment: TypeAlias = MutableMapping[str, Any]


class StartResponse(Protocol):
    def __call__(self, __status: str, __headers: Headers, __exc_info: ExcInfo | None = ..., /) -> Any: ...


class InputStream(Iterable[bytes], Protocol):
    def read(self, __size: int = ..., /) -> bytes: ...
    def readline(self, __size: int = ..., /) -> bytes: ...
    def readlines(self, __hint: int = ..., /) -> Iterator[bytes]: ...
