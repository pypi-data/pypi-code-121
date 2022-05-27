"""The module that defines the ``BaseLTIProvider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class BaseLTIProvider:
    """The base JSON representation for an LTI 1.1 provider."""

    #: The id of this LTI provider.
    id: "str"
    #: The time this LTI provider was created.
    created_at: "datetime.datetime"
    #: Who will use this LTI provider.
    intended_use: "str"
    #: The id of the tenant that owns this provider.
    tenant_id: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of this LTI provider.",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The time this LTI provider was created.",
            ),
            rqa.RequiredArgument(
                "intended_use",
                rqa.SimpleValue.str,
                doc="Who will use this LTI provider.",
            ),
            rqa.RequiredArgument(
                "tenant_id",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The id of the tenant that owns this provider.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "intended_use": to_dict(self.intended_use),
            "tenant_id": to_dict(self.tenant_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseLTIProvider"], d: t.Dict[str, t.Any]
    ) -> "BaseLTIProvider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            created_at=parsed.created_at,
            intended_use=parsed.intended_use,
            tenant_id=parsed.tenant_id,
        )
        res.raw_data = d
        return res
