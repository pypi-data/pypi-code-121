"""This module contains a parser for nullable values.
"""
import typing as t

from ._base import Parser
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from .exceptions import SimpleParseError
from ._swagger_utils import OpenAPISchema

__all__ = ('Nullable', )


class Nullable(t.Generic[_T], Parser[t.Union[_T, None]]):
    """Make a parser that also allows ``None`` values.
    """
    if _USE_SLOTS:
        __slots__ = ('__parser', )

    def __init__(self, parser: Parser[_T]):
        super().__init__()
        self.__parser = parser

    def describe(self) -> str:
        return f'Union[None, {self.__parser.describe()}]'

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return self.__parser.to_open_api(schema)

    def to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        res = super().to_open_api(schema)
        return {**res, 'nullable': True}

    def try_parse(self, value: object) -> t.Optional[_T]:
        if value is None:
            return value

        try:
            return self.__parser.try_parse(value)
        except SimpleParseError as err:
            raise SimpleParseError(self, value) from err
