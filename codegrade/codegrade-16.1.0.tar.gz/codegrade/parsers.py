"""Utils used for parsing data.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import sys
import typing as t

import cg_request_args as rqa
from httpx import Response

if sys.version_info >= (3, 8):
    from typing import Protocol
else:  # pragma: no cover
    from typing_extensions import Protocol

ModelLikeT = t.TypeVar("ModelLikeT", bound="ModelLike")
_T = t.TypeVar("_T")


class ModelLike(Protocol):
    data_parser: t.ClassVar[rqa.Parser]

    @classmethod
    def from_dict(cls, d: t.Dict[str, t.Any]) -> t.Any:
        ...


class ParserFor(rqa.Parser[ModelLikeT], t.Generic[ModelLikeT]):  # type: ignore
    __slots__ = ("model",)

    _BASE = t.cast(
        rqa.Parser[t.Dict[str, t.Any]], rqa.LookupMapping(rqa.AnyValue)
    )
    _SEEN_PARSERS: t.Dict[t.Type, t.Any] = {}

    def __init__(self, model: t.Type[ModelLikeT]) -> None:
        super().__init__()
        self.model = model

    @classmethod
    def make(cls, model: t.Type[ModelLikeT]) -> "ParserFor[ModelLikeT]":
        if model not in cls._SEEN_PARSERS:
            cls._SEEN_PARSERS[model] = cls(model)
        return cls._SEEN_PARSERS[model]

    def describe(self) -> str:
        return self.model.data_parser.describe()

    def _to_open_api(self, schema: t.Any) -> t.Mapping[str, t.Any]:
        return self.model.data_parser.to_open_api(schema)

    def try_parse(self, value: object) -> t.Any:
        dct = self._BASE.try_parse(value)

        try:
            return self.model.from_dict(dct)
        except rqa.ParseError as exc:
            raise exc
        except BaseException as exc:
            raise rqa.SimpleParseError(self, value) from exc


class BaseResponseParser(rqa.Parser[_T], t.Generic[_T]):  # type: ignore
    __slots__ = ()

    def _try_parse_response(self, value: Response) -> _T:
        raise NotImplementedError

    def try_parse(self, value: object) -> _T:
        if not isinstance(value, Response):
            raise rqa.SimpleParseError(self, value)

        return self._try_parse_response(value)


class JsonResponseParser(BaseResponseParser[_T], t.Generic[_T]):
    __slots__ = ("_parser",)
    _SEEN_PARSERS: t.Dict[rqa.Parser, "JsonResponseParser"] = {}

    def __init__(self, parser: rqa.Parser[_T]):
        self._parser = parser

    @classmethod
    def make(cls, parser: rqa.Parser[_T]) -> "JsonResponseParser[_T]":
        if parser not in cls._SEEN_PARSERS:
            cls._SEEN_PARSERS[parser] = cls(parser)
        return cls._SEEN_PARSERS[parser]

    def describe(self) -> str:
        return self._parser.describe()

    def _to_open_api(self, schema: t.Any) -> t.Mapping[str, t.Any]:
        return self._parser.to_open_api(schema)

    def _try_parse_response(self, value: Response) -> _T:
        return self._parser.try_parse(value.json())


class ResponsePropertyParser(BaseResponseParser[_T], t.Generic[_T]):
    __slots__ = ("_prop", "_call")

    def __init__(self, prop: str, call: t.Callable[[t.Any], _T]):
        self._prop = prop
        self._call = call

    def describe(self) -> str:
        return f"Parser for response.{self._prop}"

    def _to_open_api(self, schema: t.Any) -> t.Mapping[str, t.Any]:
        return {}

    def _try_parse_response(self, value: Response) -> _T:
        try:
            return self._call(getattr(value, self._prop))
        except:
            raise rqa.SimpleParseError(self, value)


class ConstantlyParser(rqa.Parser[_T], t.Generic[_T]):  # type: ignore
    __slots__ = ("_value",)

    def __init__(self, value: _T):
        self._value = value

    def describe(self) -> str:
        return f"Constantly {self._value}"

    def _to_open_api(self, schema: t.Any) -> t.Mapping[str, t.Any]:
        return {}

    def try_parse(self, value: object) -> _T:
        return self._value


def make_union(*parsers: rqa.Parser) -> rqa.Parser:
    res, *rest = parsers
    for cur in rest:
        res |= cur
    return res
