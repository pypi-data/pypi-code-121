"""This module contains various utils to make parsing values easier.
"""
import abc
import typing as t

from ._base import Parser as _Parser
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from ._utils import Y as _Y
from .exceptions import SimpleParseError as _SimpleParseError
from ._swagger_utils import OpenAPISchema

__all__ = ('Transform', 'Constraint')


class Transform(t.Generic[_T, _Y], _Parser[_T], abc.ABC):
    """Make a parser that transforms the result from another parser.
    """
    if _USE_SLOTS:
        __slots__ = ('_parser', '__transform', '__transform_name')

    def __init__(
        self,
        parser: _Parser[_Y],
        transform: t.Callable[[_Y], _T],
        transform_name: str,
    ):
        super().__init__()
        self._parser = parser
        self.__transform = transform
        self.__transform_name = transform_name

    def describe(self) -> str:
        return f'{self.__transform_name} as {self._parser.describe()}'

    def try_parse(self, value: object) -> _T:
        res = self._parser.try_parse(value)
        return self.__transform(res)


class Constraint(t.Generic[_T], _Parser[_T]):
    """Parse a value, and further constrain the allowed values.
    """
    if _USE_SLOTS:
        __slots__ = ('_parser', )

    def __init__(self, parser: _Parser[_T]):
        super().__init__()
        self._parser = parser

    @abc.abstractmethod
    def ok(self, value: _T) -> bool:
        """Check if the given value passes the constraint.
        """
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the constraint, used for error messages.
        """
        ...

    def describe(self) -> str:
        return f'{self._parser.describe()} {self.name}'

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return self._parser.to_open_api(schema)

    def try_parse(self, value: object) -> _T:
        res = self._parser.try_parse(value)
        if not self.ok(res):
            raise _SimpleParseError(self, value)
        return res
