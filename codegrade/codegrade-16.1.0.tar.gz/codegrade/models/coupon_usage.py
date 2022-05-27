"""The module that defines the ``CouponUsage`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .coupon import Coupon, CouponParser


@dataclass
class CouponUsage:
    """A link that represents the usage of a coupon by a user."""

    #: The id of the coupon usage
    id: "str"
    #: The moment the coupon was used.
    created_at: "datetime.datetime"
    coupon: "Coupon"
    #: The user that used the coupon.
    user_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the coupon usage",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment the coupon was used.",
            ),
            rqa.RequiredArgument(
                "coupon",
                CouponParser,
                doc="",
            ),
            rqa.RequiredArgument(
                "user_id",
                rqa.SimpleValue.int,
                doc="The user that used the coupon.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "coupon": to_dict(self.coupon),
            "user_id": to_dict(self.user_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CouponUsage"], d: t.Dict[str, t.Any]
    ) -> "CouponUsage":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            created_at=parsed.created_at,
            coupon=parsed.coupon,
            user_id=parsed.user_id,
        )
        res.raw_data = d
        return res
