"""
This module contains a parser that makes it possible to lazily construct
another parser.
"""
import typing as t
import threading

from ._base import Parser
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from ._swagger_utils import OpenAPISchema

__all__ = ('Lazy', )


class Lazy(t.Generic[_T], Parser[_T]):
    """A wrapping parser that allows you to construct circular parsers.

    The method ``make_parser`` will be executed when you first try to parse
    something. It will only be executed once.
    """
    _LOCK = threading.RLock()

    if _USE_SLOTS:
        __slots__ = ('_parser', '_make_parser')

    def __init__(self, make_parser: t.Callable[[], Parser[_T]]):
        super().__init__()
        self._parser: t.Optional[Parser[_T]] = None
        self._make_parser = make_parser

    @property
    def parser(self) -> Parser[_T]:
        """The parser that this lazy uses.
        """
        if self._parser is None:
            with self._LOCK:
                if self._parser is None:
                    self._parser = self._make_parser()
        return self._parser

    def describe(self) -> str:
        return self.parser.describe()

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return self.parser._to_open_api(schema)  # pylint: disable=protected-access

    def try_parse(self, value: object) -> _T:
        return self.parser.try_parse(value)
