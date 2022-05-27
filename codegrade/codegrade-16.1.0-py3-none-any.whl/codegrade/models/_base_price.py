"""The module that defines the ``_BasePrice`` model.

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
class _BasePrice:
    """The base of a price."""

    #: The id of the price.
    id: "str"
    #: The currency this price is in.
    currency: "Currency"
    #: The amount of the above currency the price is.
    amount: "str"
    #: The amount of time you have to ask for a refund.
    refund_period: "datetime.timedelta"
    #: Is tax included or excluded in the price?
    tax_behavior: "TaxBehavior"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the price.",
            ),
            rqa.RequiredArgument(
                "currency",
                rqa.EnumValue(Currency),
                doc="The currency this price is in.",
            ),
            rqa.RequiredArgument(
                "amount",
                rqa.SimpleValue.str,
                doc="The amount of the above currency the price is.",
            ),
            rqa.RequiredArgument(
                "refund_period",
                rqa.RichValue.TimeDelta,
                doc="The amount of time you have to ask for a refund.",
            ),
            rqa.RequiredArgument(
                "tax_behavior",
                rqa.EnumValue(TaxBehavior),
                doc="Is tax included or excluded in the price?",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "currency": to_dict(self.currency),
            "amount": to_dict(self.amount),
            "refund_period": to_dict(self.refund_period),
            "tax_behavior": to_dict(self.tax_behavior),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["_BasePrice"], d: t.Dict[str, t.Any]
    ) -> "_BasePrice":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            currency=parsed.currency,
            amount=parsed.amount,
            refund_period=parsed.refund_period,
            tax_behavior=parsed.tax_behavior,
        )
        res.raw_data = d
        return res
