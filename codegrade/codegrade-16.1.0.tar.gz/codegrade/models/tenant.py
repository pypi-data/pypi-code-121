"""The module that defines the ``Tenant`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .tenant_statistics import TenantStatistics


@dataclass
class Tenant:
    """The JSON representation of a tenant."""

    #: The id of the tenant
    id: "str"
    #: The name of the tenant
    name: "str"
    #: Maybe the id of the SSO provider connected to this tenant.
    sso_provider_id: "t.Optional[str]"
    #: Maybe the statistics of this tenant, if requested and if you have the
    #: permission to see it.
    statistics: "t.Optional[TenantStatistics]"
    #: The short name (or names) of the tenant. This is used to make searching
    #: for tenants by end users easier.
    abbreviated_name: "t.Optional[str]"
    #: This value determines how the tenant should be ordered. Tenants should
    #: first be ordered from highest `order_category` to lowest, and then by
    #: name.
    order_category: "int"
    #: The netloc this tenant is hosted on.
    netloc: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the tenant",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the tenant",
            ),
            rqa.RequiredArgument(
                "sso_provider_id",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "Maybe the id of the SSO provider connected to this"
                    " tenant."
                ),
            ),
            rqa.RequiredArgument(
                "statistics",
                rqa.Nullable(parsers.ParserFor.make(TenantStatistics)),
                doc=(
                    "Maybe the statistics of this tenant, if requested and if"
                    " you have the permission to see it."
                ),
            ),
            rqa.RequiredArgument(
                "abbreviated_name",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The short name (or names) of the tenant. This is used to"
                    " make searching for tenants by end users easier."
                ),
            ),
            rqa.RequiredArgument(
                "order_category",
                rqa.SimpleValue.int,
                doc=(
                    "This value determines how the tenant should be ordered."
                    " Tenants should first be ordered from highest"
                    " `order_category` to lowest, and then by name."
                ),
            ),
            rqa.RequiredArgument(
                "netloc",
                rqa.SimpleValue.str,
                doc="The netloc this tenant is hosted on.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "sso_provider_id": to_dict(self.sso_provider_id),
            "statistics": to_dict(self.statistics),
            "abbreviated_name": to_dict(self.abbreviated_name),
            "order_category": to_dict(self.order_category),
            "netloc": to_dict(self.netloc),
        }
        return res

    @classmethod
    def from_dict(cls: t.Type["Tenant"], d: t.Dict[str, t.Any]) -> "Tenant":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            name=parsed.name,
            sso_provider_id=parsed.sso_provider_id,
            statistics=parsed.statistics,
            abbreviated_name=parsed.abbreviated_name,
            order_category=parsed.order_category,
            netloc=parsed.netloc,
        )
        res.raw_data = d
        return res
