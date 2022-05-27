"""This module defines some util function for ``cg_request_args``.

It should not be used outside the ``cg_request_args`` module.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import sys
import typing as t

try:
    from cg_helpers import readable_join  # pylint: disable=unused-import
except ImportError:  # pragma: no cover

    def readable_join(lst: t.Sequence[str]) -> str:
        """Simple implementation of ``readable_join``.
        """
        return ', '.join(lst)


if sys.version_info >= (3, 8):
    # pylint: disable=unused-import
    from typing import Final, Literal, Protocol, TypedDict
else:  # pragma: no cover
    from typing_extensions import Final, Literal, Protocol, TypedDict


def _issubclass(value: t.Any, cls: t.Type) -> bool:
    return isinstance(value, type) and issubclass(value, cls)


def is_typeddict(value: object) -> bool:
    """Check if the given value is a TypedDict.
    """
    return _issubclass(value, dict) and hasattr(value, '__total__')


USE_SLOTS = sys.version_info >= (3, 7)

_TYPE_NAME_LOOKUP = {
    str: 'str',
    float: 'float',
    bool: 'bool',
    int: 'int',
    dict: 'mapping',
    list: 'list',
    type(None): 'null',
}


def type_to_name(typ: t.Type) -> str:
    """Convert the given type to a string.
    """
    if typ in _TYPE_NAME_LOOKUP:
        return _TYPE_NAME_LOOKUP[typ]
    return str(typ)  # pragma: no cover


T_COV = t.TypeVar('T_COV', covariant=True)  # pylint: disable=invalid-name
T = t.TypeVar('T')
Y = t.TypeVar('Y')
