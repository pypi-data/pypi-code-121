"""The module that defines the ``CouponWithCode`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_coupon import BaseCoupon


@dataclass
class CouponWithCode(BaseCoupon):
    """A coupon where you do have the permission to see the code."""

    #: This is a coupon with code.
    type: "t.Literal['coupon-with-code']"
    #: The code of the coupon.
    code: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseCoupon.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "type",
                    rqa.StringEnum("coupon-with-code"),
                    doc="This is a coupon with code.",
                ),
                rqa.RequiredArgument(
                    "code",
                    rqa.SimpleValue.str,
                    doc="The code of the coupon.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "code": to_dict(self.code),
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "limit": to_dict(self.limit),
            "used_amount": to_dict(self.used_amount),
            "course_price": to_dict(self.course_price),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CouponWithCode"], d: t.Dict[str, t.Any]
    ) -> "CouponWithCode":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            code=parsed.code,
            id=parsed.id,
            created_at=parsed.created_at,
            limit=parsed.limit,
            used_amount=parsed.used_amount,
            course_price=parsed.course_price,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .course_price import CoursePrice

    # fmt: on
