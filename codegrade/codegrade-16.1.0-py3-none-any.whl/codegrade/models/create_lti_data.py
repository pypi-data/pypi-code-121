"""The module that defines the ``CreateLTIData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .lti1p1_provider_data import LTI1p1ProviderData
from .lti1p3_provider_data import LTI1p3ProviderData

CreateLTIData = t.Union[
    LTI1p1ProviderData,
    LTI1p3ProviderData,
]
CreateLTIDataParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(LTI1p1ProviderData), ParserFor.make(LTI1p3ProviderData)
    ),
)
