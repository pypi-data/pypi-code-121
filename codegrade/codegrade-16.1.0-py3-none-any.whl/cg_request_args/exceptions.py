"""This module contains the exceptions used by the ``cg_request_args`` module.
"""
import copy
import typing as t

import cg_maybe

from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import Protocol, readable_join

__all__ = ('ParseError', 'SimpleParseError', 'MultipleParseErrors')

_ParserErrorT = t.TypeVar('_ParserErrorT', bound='ParseError')


class _ParserLike(Protocol):
    def describe(self) -> str:
        ...


class ParseError(ValueError):
    """Error raised when a parser fails.
    """
    if _USE_SLOTS:
        __slots__ = ('parser', 'found', 'extra', 'location', '__as_string')

    def __init__(
        self,
        parser: '_ParserLike',
        found: object,
        *,
        extra: t.Mapping[str, str] = None
    ):
        super().__init__()
        self.parser = parser
        self.found = found
        self.extra = {} if extra is None else extra
        self.location: t.Sequence[t.Union[int, str]] = []
        self.__as_string: t.Optional[str] = None

    def _loc_to_str(self) -> str:
        res = []
        for idx, loc in enumerate(self.location):
            if idx == 0:
                res.append(str(loc))
            elif isinstance(loc, int):
                res.append('[{}]'.format(loc))
            else:
                res.append('.{}'.format(loc))

        return ''.join(res)

    def __str__(self) -> str:
        if self.__as_string is None:
            res = f'{self._to_str()}.'
            self.__as_string = f'{res[0].upper()}{res[1:]}'
        return self.__as_string

    def _to_str(self) -> str:
        got = repr(self.found)
        described = self.parser.describe()

        if described[0].lower() in ('a', 'i', 'e', 'u'):
            prefix = 'an'
        else:
            prefix = 'a'
        base = '{} {} is required, but got {}'.format(prefix, described, got)

        if self.extra.get('message') is not None:
            base = f'{base} ({self.extra["message"]})'

        if self.location:
            return 'at index "{}" {}'.format(self._loc_to_str(), base)
        return base

    def __copy__(self: _ParserErrorT) -> _ParserErrorT:
        res = type(self)(self.parser, self.found, extra=self.extra)
        res.location = self.location
        return res

    def add_location(
        self: _ParserErrorT, location: t.Union[int, str]
    ) -> _ParserErrorT:
        """Get a new error with the added location.
        """
        res = copy.copy(self)
        res.location = [location, *res.location]
        return res

    def to_dict(self) -> t.Mapping[str, t.Any]:
        """Convert the error to a dictionary.
        """
        found: t.Union[str, t.Mapping[str, t.Any]]
        if cg_maybe.Nothing.is_nothing_instance(self.found):
            found = 'Nothing'
        else:
            found = {
                'value': self.found,
                'type': type(self.found).__name__,
            }
        return {
            'found': found,
            'expected': self.parser.describe(),
        }


class SimpleParseError(ParseError):
    """The parse error raised when the value was incorrect.
    """


class MultipleParseErrors(ParseError):
    """The parse error raised when the container type the value was correct,
    but the values contained parse errors.
    """
    def __init__(
        self,
        parser: '_ParserLike',
        found: object,
        errors: t.Sequence[ParseError] = None,
        *,
        extra: t.Mapping[str, str] = None,
    ):
        super().__init__(parser, found, extra=extra)
        self.errors = [] if errors is None else errors

    def __copy__(self) -> 'MultipleParseErrors':
        res = super().__copy__()
        res.errors = self.errors
        return res

    def _to_str(self) -> str:
        res = super()._to_str()
        if not self.errors:  # pragma: no cover
            # In this case you shouldn't really use this class.
            return res
        reasons = readable_join([err._to_str() for err in self.errors])  # pylint: disable=protected-access
        return f'{res}, which is incorrect because {reasons}'

    def to_dict(self) -> t.Mapping[str, t.Any]:
        return {
            **super().to_dict(),
            'sub_errors': [{
                'error': err.to_dict(),
                'location': err.location,
            } for err in self.errors],
        }
