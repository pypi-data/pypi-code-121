"""The module that defines the ``StartPaymentCoursePriceData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .start_payment_course_price_close_tab_data import (
    StartPaymentCoursePriceCloseTabData,
)
from .start_payment_course_price_redirect_data import (
    StartPaymentCoursePriceRedirectData,
)

StartPaymentCoursePriceData = t.Union[
    StartPaymentCoursePriceRedirectData,
    StartPaymentCoursePriceCloseTabData,
]
StartPaymentCoursePriceDataParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(StartPaymentCoursePriceRedirectData),
        ParserFor.make(StartPaymentCoursePriceCloseTabData),
    ),
)
