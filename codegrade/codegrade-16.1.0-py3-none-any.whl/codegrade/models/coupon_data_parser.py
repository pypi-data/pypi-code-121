"""The module that defines the ``CouponDataParser`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CouponDataParser:
    """The data to update or create a new coupon"""

    #: The amount of users that can use this coupon, if `None` it is unlimited.
    limit: "t.Optional[int]"
    #: The code the user should use for the coupon.
    code: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "limit",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The amount of users that can use this coupon, if `None`"
                    " it is unlimited."
                ),
            ),
            rqa.RequiredArgument(
                "code",
                rqa.SimpleValue.str,
                doc="The code the user should use for the coupon.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "limit": to_dict(self.limit),
            "code": to_dict(self.code),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CouponDataParser"], d: t.Dict[str, t.Any]
    ) -> "CouponDataParser":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            limit=parsed.limit,
            code=parsed.code,
        )
        res.raw_data = d
        return res
