"""This module combines ``Just`` and ``Nothing`` into ``Maybe``.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import typing as t

from ._just import Just
from ._nothing import _Nothing

_Nothing._set_doc()  # pylint: disable=protected-access

_T = t.TypeVar('_T', covariant=True)

Maybe = t.Union[Just[_T], _Nothing[_T]]
