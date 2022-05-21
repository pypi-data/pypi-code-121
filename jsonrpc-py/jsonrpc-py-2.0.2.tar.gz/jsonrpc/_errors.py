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

from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Any, Final, SupportsInt

from ._utilities import Undefined, UndefinedType, make_hashable

__all__: Final[list[str]] = ["Error", "ErrorEnum"]


class ErrorEnum(IntEnum):
    """
    An enumeration of error codes that indicates the error type that occurred.
    """
    #: Error occurred due the serialization to JSON or deserialization from JSON.
    PARSE_ERROR: int = -32700
    #: Error occurred due the receiving an invalid :class:`jsonrpc.Request` object.
    INVALID_REQUEST: int = -32600
    #: Error occurred due the invoking a missing user-function.
    METHOD_NOT_FOUND: int = -32601
    #: Error occurred due the receiving an invalid user-function's arguments.
    INVALID_PARAMETERS: int = -32602
    #: Error occurred due the unexpected internal errors.
    INTERNAL_ERROR: int = -32603


class BaseError(Exception, metaclass=ABCMeta):
    __slots__: tuple[str, ...] = ()

    @property
    @abstractmethod
    def code(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def message(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def data(self) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def json(self) -> dict[str, Any]:
        raise NotImplementedError


class Error(BaseError):
    """
    An object representing a common exception for all encountered errors in the JSON-RPC protocol.
    This object can be used in user-defined functions to throw user-defined exception with the custom error code for example.
    """
    __slots__: list[str] = ["_code", "_message", "_data"]

    def __init__(self, *, code: SupportsInt, message: str, data: Any = Undefined) -> None:
        super(Error, self).__init__(message)
        self._code: Final[int] = int(code)
        self._message: Final[str] = str(message)
        self._data: Final[Any] = data

    def __str__(self) -> str:
        return f"{self._message!s}\u0020\u0028{self._code:d}\u0029"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" \
            f"code={self._code!r}, " \
            f"message={self._message!r}, " \
            f"data={self._data!r})>"

    def __hash__(self) -> int:
        return hash(self._code) ^ hash(self._message) ^ hash(make_hashable(self._data))

    def __eq__(self, obj: Any, /) -> bool:
        return isinstance(obj, self.__class__) \
            and type(self._code) == type(obj._code) and self._code == obj._code \
            and type(self._message) == type(obj._message) and self._message == obj._message \
            and type(self._data) == type(obj._data) and self._data == obj._data

    @property
    def code(self) -> int:
        """
        The :py:class:`int` object, or any object that passing by :py:class:`typing.SupportsInt`,
        that indicates the error type that occurred.
        Possible error codes you can find in the :class:`jsonrpc.ErrorEnum` enumeration.
        """
        return self._code

    @property
    def message(self) -> str:
        """
        A string providing a short description of the error.
        This attribute should be limited to a concise single sentence.
        """
        return self._message

    @property
    def data(self) -> Any:
        """
        An any type of object that contains additional information about the error.
        It must be JSON serializable.
        If its value omitted, this attribute doesn't participate to JSON serialization.

        .. warning::
            Remember that :py:data:`None` is a valid value for this attribute.
            This means that this attribute isn't omitted and will be participate in JSON serialization.
        """
        return self._data

    @property
    def json(self) -> dict[str, Any]:
        """
        Returns the :py:class:`dict` object needed for JSON serialization.
        Primarily used by the :class:`jsonrpc.Request` object.

        Example output::

            >>> error: Error = Error(code=ErrorEnum.INTERNAL_ERROR, message="Unexpected error", data={
            ...     "additional": "information"
            ... })
            >>> error.json
            {"code": -32603, "message": "Unexpected error", "data": {"additional": "information"}}
        """
        obj: dict[str, Any] = {"code": self._code, "message": self._message}

        if not isinstance(data := self._data, UndefinedType):
            obj |= {"data": data}

        return obj
