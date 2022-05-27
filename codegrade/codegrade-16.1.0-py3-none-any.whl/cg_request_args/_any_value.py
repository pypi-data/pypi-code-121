"""Parse any value into the ``Any`` type.
"""
import typing as _t

from ._base import Parser as _Parser
from ._swagger_utils import OpenAPISchema as _OpenAPISchema

__all__ = ('AnyValue', )


class _AnyValue(_Parser[_t.Any]):
    """A validator for an ``Any`` value. This will allow any value.
    """
    @staticmethod
    def describe() -> str:
        """The description for the any parser.
        """
        return 'Any'

    @staticmethod
    def _to_open_api(_: _OpenAPISchema) -> _t.Mapping[str, _t.Any]:
        return {}

    @staticmethod
    def try_parse(value: object) -> _t.Any:
        """Parse the given value, this is basically a cast to ``Any``.
        """
        return value


AnyValue = _AnyValue()
