"""This module implements the ``Maybe`` monad.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from . import utils
from ._just import Just
from .utils import of, from_nullable
from ._maybe import Maybe
from ._nothing import Nothing, _Nothing
