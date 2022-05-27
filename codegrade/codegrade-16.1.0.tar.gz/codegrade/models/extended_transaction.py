"""The module that defines the ``ExtendedTransaction`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_price import CoursePrice
from .transaction import Transaction


@dataclass
class ExtendedTransaction(Transaction):
    """The extended version of a transaction."""

    #: The `CoursePrice` that this transaction pays for.
    course_price: "CoursePrice"
    #: The short id of the transaction.
    short_id: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: Transaction.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "course_price",
                    parsers.ParserFor.make(CoursePrice),
                    doc="The `CoursePrice` that this transaction pays for.",
                ),
                rqa.RequiredArgument(
                    "short_id",
                    rqa.SimpleValue.str,
                    doc="The short id of the transaction.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "course_price": to_dict(self.course_price),
            "short_id": to_dict(self.short_id),
            "id": to_dict(self.id),
            "state": to_dict(self.state),
            "course_price_id": to_dict(self.course_price_id),
            "success_at": to_dict(self.success_at),
            "updated_at": to_dict(self.updated_at),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedTransaction"], d: t.Dict[str, t.Any]
    ) -> "ExtendedTransaction":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            course_price=parsed.course_price,
            short_id=parsed.short_id,
            id=parsed.id,
            state=parsed.state,
            course_price_id=parsed.course_price_id,
            success_at=parsed.success_at,
            updated_at=parsed.updated_at,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .transaction_state import TransactionState

    # fmt: on
