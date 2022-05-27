"""This module contains parsers for various lists kinds.
"""
import typing as t

from ._base import Parser
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from ._utils import Y as _Y
from ._utils import Final
from .exceptions import ParseError, SimpleParseError, MultipleParseErrors
from ._swagger_utils import OpenAPISchema

__all__ = ('List', 'TwoTuple')


class List(t.Generic[_T], Parser[t.Sequence[_T]]):
    """A parser for a list homogeneous values.
    """
    if _USE_SLOTS:
        __slots__ = ('__el_type', )

    def __init__(self, el_type: Parser[_T]):
        super().__init__()
        self.__el_type: Final = el_type

    def describe(self) -> str:
        return f'List[{self.__el_type.describe()}]'

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {
            'type': 'array',
            'items': self.__el_type.to_open_api(schema),
        }

    def try_parse(self, value: object) -> t.List[_T]:
        if not isinstance(value, list):
            raise SimpleParseError(self, value)

        el_type = self.__el_type
        res = []
        errors = []

        for idx, item in enumerate(value):
            try:
                res.append(el_type.try_parse(item))
            except ParseError as e:
                errors.append(e.add_location(idx))

        if errors:
            raise MultipleParseErrors(self, value, errors)
        else:
            return res


class TwoTuple(t.Generic[_T, _Y], Parser[t.Tuple[_T, _Y]]):
    """A parser for a tuple that consists exactly of two arguments.
    """

    if _USE_SLOTS:
        __slots__ = ('__left', '__right')

    def __init__(self, left: Parser[_T], right: Parser[_Y]) -> None:
        super().__init__()
        self.__left = left
        self.__right = right

    def describe(self) -> str:
        return 'Tuple[{}, {}]'.format(
            self.__left.describe(), self.__right.describe()
        )

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {
            'type': 'array',
            'items': (self.__left | self.__right).to_open_api(schema),
            'minItems': 2,
            'maxItems': 2,
        }

    def try_parse(self, value: object) -> t.Tuple[_T, _Y]:
        if not isinstance(value, (tuple, list)):
            raise SimpleParseError(self, value)
        if len(value) != 2:
            raise SimpleParseError(self, value)

        return (
            self.__left.try_parse(value[0]),
            self.__right.try_parse(value[1]),
        )
