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
from collections.abc import Iterable, Iterator
from numbers import Number
from types import NoneType
from typing import Any, Final, TypeVar, overload

from ._errors import Error
from ._utilities import Undefined, UndefinedType, make_hashable, partition

__all__: Final[list[str]] = ["BatchResponse", "Response"]

_T = TypeVar("_T")


class BaseResponse(metaclass=ABCMeta):
    __slots__: tuple[str, ...] = ()

    @property
    @abstractmethod
    def body(self) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def error(self) -> Error:
        raise NotImplementedError

    @property
    @abstractmethod
    def response_id(self) -> str | Number | UndefinedType | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_successful(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def json(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseBatchResponse(Iterable[BaseResponse]):
    __slots__: tuple[str, ...] = ()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def json(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class Response(BaseResponse):
    """
    Base JSON-RPC response object.

    :param body: An any type of object that contains a result of successful processing
        the :class:`jsonrpc.Request` object. This attribute must not be set if there an error has occurred.
    :param error: The :class:`jsonrpc.Error` object representing an erroneous processing
        the :class:`jsonrpc.Request` object. This attribute must not be set if no one error has occurred.
    :param response_id: The same attribute as :attr:`jsonrpc.Request.request_id`
        except that its value might be equal to :py:data:`None` in erroneous responses.
    :raises TypeError: If both or no one ``body`` or ``error`` attributes are set
        or response identifier isn't the same type as request identifier.
    """
    __slots__: list[str] = ["_body", "_error", "_id"]

    @overload
    def __init__(self, *,
        body: Any,
        response_id: str | Number | UndefinedType | None = ...
    ) -> None: ...

    @overload
    def __init__(self, *,
        error: Error,
        response_id: str | Number | UndefinedType | None = ...
    ) -> None: ...

    def __init__(self, *,
        body: Any = Undefined,
        error: Error | UndefinedType = Undefined,
        response_id: str | Number | UndefinedType | None = Undefined
    ) -> None:
        self._is_body_and_error_valid(body=body, error=error)
        self._body: Final[Any] = body
        self._error: Final[Error | UndefinedType] = error
        self._id: Final[str | Number | UndefinedType | None] = self._is_response_id_valid(response_id=response_id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" \
            f"body={self._body!r}, " \
            f"error={self._error!r}, " \
            f"response_id={self._id!r})>"

    def __hash__(self) -> int:
        return hash(make_hashable(self._body)) ^ hash(self._error) ^ hash(self._id)

    def __eq__(self, obj: Any, /) -> bool:
        return isinstance(obj, self.__class__) \
            and type(self._body) == type(obj._body) and self._body == obj._body \
            and type(self._error) == type(obj._error) and self._error == obj._error \
            and type(self._id) == type(obj._id) and self._id == obj._id

    def _is_body_and_error_valid(self, *, body: Any, error: Error | UndefinedType) -> None:
        if isinstance(body, UndefinedType) == isinstance(error, UndefinedType):
            raise TypeError("Either \"body\" or \"error\" attribute must be set")

    def _is_response_id_valid(self, *, response_id: _T) -> _T:
        if not isinstance(response_id, str | Number | UndefinedType | NoneType):
            raise TypeError(f"Response id must be an optional string or number, not a {type(response_id).__name__!r}")

        return response_id

    @property
    def body(self) -> Any:
        """
        An any type of object that contains the payload of the successful response.
        It must be JSON serializable.

        :raises AttributeError: If the response is erroneous.
        """
        if not self.is_successful:
            raise AttributeError("Erroneous response hasn't \"body\" attribute")

        return self._body

    @property
    def error(self) -> Error:
        """
        Returns the :class:`jsonrpc.Error` object containing the payload of the erroneous response.

        :raises AttributeError: If the response is successful.
        """
        if self.is_successful:
            raise AttributeError("Successful response hasn't \"error\" attribute")

        return self._error

    @property
    def response_id(self) -> str | Number | UndefinedType | None:
        """
        Returns the :py:class:`str` object or any type of :py:class:`numbers.Number` object
        representing the identifier of the response.
        In cases erroneous responses its value might be equal to :py:data:`None`.
        """
        return self._id

    @property
    def is_successful(self) -> bool:
        """
        Returns :py:data:`True` if the ``body`` attribute isn't omitted in the class constructor
        and the ``error`` attribute isn't set, :py:data:`False` elsewise.
        """
        return not isinstance(self._body, UndefinedType) and isinstance(self._error, UndefinedType)

    @property
    def json(self) -> dict[str, Any]:
        """
        Returns the :py:class:`dict` object needed for JSON serialization.
        Primarily used by the :class:`jsonrpc.WSGIHandler` instance.

        Example successful response::

            >>> response: Response = Response(body="foobar", response_id=65535)
            >>> response.json
            {"jsonrpc": "2.0", "result": "foobar", "id": 65535}

        Example erroneous response::

            >>> error: Error = Error(code=ErrorEnum.INTERNAL_ERROR, message="Unexpected error")
            >>> response: Response = Response(error=error, response_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8")
            >>> response.json
            {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Unexpected error"}, "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"}
        """
        obj: dict[str, Any] = {"jsonrpc": "2.0"}

        try:
            obj |= {"result": self.body}
        except AttributeError:
            obj |= {"error": self.error.json}
        if not isinstance(response_id := self._id, UndefinedType):
            obj |= {"id": response_id}

        return obj


class BatchResponse(BaseBatchResponse[Response]):
    """
    The :py:class:`collections.abc.Iterable` subclass representing the unordered collection
    of :class:`jsonrpc.Response` unique objects.
    """
    __slots__: list[str] = ["_responses"]

    def __init__(self, responses: Iterable[Response], /) -> None:
        self._responses: Final[frozenset[Response]] = frozenset(responses)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(\u2026)>"

    def __hash__(self) -> int:
        return hash(self._responses) ^ len(self._responses)

    def __eq__(self, obj: Any, /) -> bool:
        return isinstance(obj, self.__class__) \
            and len(self._responses) == len(obj._responses) \
            and self._responses == obj._responses

    def __iter__(self) -> Iterator[Response]:
        return partition(lambda response: response.is_successful, self._responses)

    def __len__(self) -> int:
        return len(self._responses)

    @property
    def json(self) -> list[dict[str, Any]]:
        """
        Returns the :py:class:`list` of :py:class:`dict` objects needed for JSON serialization.
        Primarily used by the :class:`jsonrpc.WSGIHandler` instance.

        Example output::

            >>> response: BatchResponse = BatchResponse([
            ...     Response(body="foobar", response_id=1024),
            ...     Response(error=Error(
            ...         code=ErrorEnum.INTERNAL_ERROR,
            ...         message="Unexpected error"
            ...     ), response_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8")
            ... ])
            >>> response.json
            [
                {"jsonrpc": "2.0", "result": "foobar", "id": 1024},
                {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Unexpected error"}, "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"}
            ]
        """
        return list(map(lambda response: response.json, self))
