"""The module that defines the ``LTI1p1Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .finalized_lti1p1_provider import FinalizedLTI1p1Provider
from .non_finalized_lti1p1_provider import NonFinalizedLTI1p1Provider

LTI1p1Provider = t.Union[
    FinalizedLTI1p1Provider,
    NonFinalizedLTI1p1Provider,
]
LTI1p1ProviderParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(FinalizedLTI1p1Provider),
        ParserFor.make(NonFinalizedLTI1p1Provider),
    ),
)
