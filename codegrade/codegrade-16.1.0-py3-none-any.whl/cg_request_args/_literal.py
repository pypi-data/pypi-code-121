"""This module contains parsers for literal values.
"""
import typing as t

from ._base import Parser, SimpleValue
from ._utils import USE_SLOTS as _USE_SLOTS
from .exceptions import SimpleParseError
from ._swagger_utils import OpenAPISchema

_BoolT = t.TypeVar('_BoolT', bound=bool)

__all__ = ('LiteralBoolean', )


class LiteralBoolean(t.Generic[_BoolT], Parser[_BoolT]):
    """A parser for a single literal boolean value.
    """
    if _USE_SLOTS:
        __slots__ = ('__value', )

    def __init__(self, value: _BoolT) -> None:
        super().__init__()
        self.__value = value

    def describe(self) -> str:
        return 'Literal[{}]'.format(self.__value)

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {
            **SimpleValue.bool.to_open_api(schema),
            'enum': [self.__value],
        }

    def try_parse(self, value: object) -> _BoolT:
        val = SimpleValue.bool.try_parse(value)
        if val != self.__value:
            raise SimpleParseError(self, value)
        return t.cast(_BoolT, val)
