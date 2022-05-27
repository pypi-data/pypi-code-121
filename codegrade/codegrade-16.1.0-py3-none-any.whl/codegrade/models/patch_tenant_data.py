"""The module that defines the ``PatchTenantData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class PatchTenantData:
    """Input data required for the `Tenant::Patch` operation."""

    #: The new name of the tenant
    name: Maybe["str"] = Nothing
    #: The new abbreviated name of the tenant
    abbreviated_name: Maybe["str"] = Nothing
    #: The new order category of the tenant
    order_category: Maybe["int"] = Nothing
    #: The new contract start date
    contract_start: Maybe["datetime.date"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.OptionalArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The new name of the tenant",
            ),
            rqa.OptionalArgument(
                "abbreviated_name",
                rqa.SimpleValue.str,
                doc="The new abbreviated name of the tenant",
            ),
            rqa.OptionalArgument(
                "order_category",
                rqa.SimpleValue.int,
                doc="The new order category of the tenant",
            ),
            rqa.OptionalArgument(
                "contract_start",
                rqa.RichValue.Date,
                doc="The new contract start date",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.name = maybe_from_nullable(self.name)
        self.abbreviated_name = maybe_from_nullable(self.abbreviated_name)
        self.order_category = maybe_from_nullable(self.order_category)
        self.contract_start = maybe_from_nullable(self.contract_start)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        if self.name.is_just:
            res["name"] = to_dict(self.name.value)
        if self.abbreviated_name.is_just:
            res["abbreviated_name"] = to_dict(self.abbreviated_name.value)
        if self.order_category.is_just:
            res["order_category"] = to_dict(self.order_category.value)
        if self.contract_start.is_just:
            res["contract_start"] = to_dict(self.contract_start.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchTenantData"], d: t.Dict[str, t.Any]
    ) -> "PatchTenantData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            abbreviated_name=parsed.abbreviated_name,
            order_category=parsed.order_category,
            contract_start=parsed.contract_start,
        )
        res.raw_data = d
        return res
