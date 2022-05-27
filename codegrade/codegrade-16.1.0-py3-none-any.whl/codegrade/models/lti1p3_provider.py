"""The module that defines the ``LTI1p3Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .finalized_lti1p3_provider import FinalizedLTI1p3Provider
from .non_finalized_lti1p3_provider import NonFinalizedLTI1p3Provider

LTI1p3Provider = t.Union[
    FinalizedLTI1p3Provider,
    NonFinalizedLTI1p3Provider,
]
LTI1p3ProviderParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(FinalizedLTI1p3Provider),
        ParserFor.make(NonFinalizedLTI1p3Provider),
    ),
)
