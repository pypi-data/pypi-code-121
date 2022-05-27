"""The module that defines the ``PutPriceTenantData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .currency import Currency
from .tax_behavior import TaxBehavior


@dataclass
class PutPriceTenantData:
    """Input data required for the `Tenant::PutPrice` operation."""

    #: The currency that should be used to pay for this course.
    currency: "Currency"
    #: The amount of the given currency this course should cost.
    amount: "str"
    #: The amount of time a user has to ask for a refund.
    refund_period: "datetime.timedelta"
    #: Is tax included in the price?
    tax_behavior: "TaxBehavior"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "currency",
                rqa.EnumValue(Currency),
                doc="The currency that should be used to pay for this course.",
            ),
            rqa.RequiredArgument(
                "amount",
                rqa.SimpleValue.str,
                doc=(
                    "The amount of the given currency this course should cost."
                ),
            ),
            rqa.RequiredArgument(
                "refund_period",
                rqa.RichValue.TimeDelta,
                doc="The amount of time a user has to ask for a refund.",
            ),
            rqa.RequiredArgument(
                "tax_behavior",
                rqa.EnumValue(TaxBehavior),
                doc="Is tax included in the price?",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "currency": to_dict(self.currency),
            "amount": to_dict(self.amount),
            "refund_period": to_dict(self.refund_period),
            "tax_behavior": to_dict(self.tax_behavior),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PutPriceTenantData"], d: t.Dict[str, t.Any]
    ) -> "PutPriceTenantData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            currency=parsed.currency,
            amount=parsed.amount,
            refund_period=parsed.refund_period,
            tax_behavior=parsed.tax_behavior,
        )
        res.raw_data = d
        return res
