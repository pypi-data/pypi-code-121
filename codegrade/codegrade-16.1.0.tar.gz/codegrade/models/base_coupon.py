"""The module that defines the ``BaseCoupon`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_price import CoursePrice


@dataclass
class BaseCoupon:
    """A coupon that can be used to pay for a course."""

    #: The id of the coupon
    id: "str"
    #: The moment the coupon was created.
    created_at: "datetime.datetime"
    #: The maximum amount of times the coupon can be used. If it is `None` the
    #: coupon can be used for an unlimited amount.
    limit: "t.Optional[int]"
    #: The amount of times it has been used.
    used_amount: "int"
    #: The `CoursePrice` this coupon pays for.
    course_price: "CoursePrice"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the coupon",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment the coupon was created.",
            ),
            rqa.RequiredArgument(
                "limit",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The maximum amount of times the coupon can be used. If it"
                    " is `None` the coupon can be used for an unlimited"
                    " amount."
                ),
            ),
            rqa.RequiredArgument(
                "used_amount",
                rqa.SimpleValue.int,
                doc="The amount of times it has been used.",
            ),
            rqa.RequiredArgument(
                "course_price",
                parsers.ParserFor.make(CoursePrice),
                doc="The `CoursePrice` this coupon pays for.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "limit": to_dict(self.limit),
            "used_amount": to_dict(self.used_amount),
            "course_price": to_dict(self.course_price),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseCoupon"], d: t.Dict[str, t.Any]
    ) -> "BaseCoupon":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            created_at=parsed.created_at,
            limit=parsed.limit,
            used_amount=parsed.used_amount,
            course_price=parsed.course_price,
        )
        res.raw_data = d
        return res
