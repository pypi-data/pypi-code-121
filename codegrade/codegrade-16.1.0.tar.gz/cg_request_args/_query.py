"""This module contains parsers for query parameters.
"""
import typing as t

from . import _parse_utils
from ._base import SimpleValue
from ._utils import readable_join as _readable_join
from .exceptions import SimpleParseError

__all__ = ('QueryParam', )


class _BoolQueryParam(_parse_utils.Transform[bool, str]):
    _TRUTHY_VALUES = ('', '1', 'true', 'yes', 't')
    _FALSY_VALUES = ('0', 'false', 'no', 'nil')
    _EXTRA_MSG = (
        'allowed truthy values are {t}; allowed falsy values are: {f}'
    ).format(
        t=_readable_join(['"{}"'.format(v) for v in _TRUTHY_VALUES]),
        f=_readable_join(['"{}"'.format(v) for v in _FALSY_VALUES]),
    )

    def __init__(self) -> None:
        super().__init__(
            SimpleValue.str,
            self.__to_bool,
            'BoolQueryParam',
        )

    def __to_bool(self, value: str) -> bool:
        lowered = value.lower()
        if lowered in self._TRUTHY_VALUES:
            return True
        elif lowered in self._FALSY_VALUES:
            return False

        raise SimpleParseError(self, value, extra={'message': self._EXTRA_MSG})

    def _to_open_api(self, schema: t.Any) -> t.Mapping[str, t.Any]:
        return SimpleValue.bool.to_open_api(schema)


class _IntQueryParam(_parse_utils.Transform[int, str]):
    def __init__(self) -> None:
        super().__init__(
            SimpleValue.str,
            self.__to_int,
            'IntQueryParam',
        )

    def __to_int(self, value: str) -> int:
        try:
            return int(value)
        except ValueError as exc:
            raise SimpleParseError(self, value) from exc

    def _to_open_api(self, schema: t.Any) -> t.Mapping[str, t.Any]:
        return SimpleValue.int.to_open_api(schema)


class QueryParam:
    """Parsers to use for query parameters.
    """
    str = SimpleValue.str
    int = _IntQueryParam()
    bool = _BoolQueryParam()
