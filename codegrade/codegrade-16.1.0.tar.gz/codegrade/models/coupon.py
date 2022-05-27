"""The module that defines the ``Coupon`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .coupon_with_code import CouponWithCode
from .coupon_without_code import CouponWithoutCode

Coupon = t.Union[
    CouponWithCode,
    CouponWithoutCode,
]
CouponParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(CouponWithCode), ParserFor.make(CouponWithoutCode)
    ),
)
