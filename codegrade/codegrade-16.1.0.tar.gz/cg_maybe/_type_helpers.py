"""Type helpers for ``cg_maybe``.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import sys
import typing as t

if sys.version_info >= (3, 8):
    # pylint: disable=unused-import
    from typing import Final, Literal, Protocol
else:  # pragma: no cover
    from typing_extensions import Final, Literal, Protocol

_T = t.TypeVar('_T', covariant=True)
_TT = t.TypeVar('_TT')


class SupportsLessThan(Protocol[_T]):
    """A type that supports the `<` operator.
    """
    def __lt__(self: _TT, other: _TT) -> bool:
        ...


class SupportsGreaterOrEqual(Protocol[_T]):
    """A type that supports the `>=` operator.
    """
    def __ge__(self: _TT, other: _TT) -> bool:
        ...
