"""The module that defines the ``CreateTenantData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers
from ..utils import to_dict
from .json_create_tenant import JsonCreateTenant
from .types import File


@dataclass
class CreateTenantData:
    """Input data required for the `Tenant::Create` operation."""

    json: "JsonCreateTenant"
    logo_default: Maybe["File"] = Nothing
    logo_dark: Maybe["File"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "json",
                parsers.ParserFor.make(JsonCreateTenant),
                doc="",
            ),
            rqa.OptionalArgument(
                "logo-default",
                rqa.AnyValue,
                doc="",
            ),
            rqa.OptionalArgument(
                "logo-dark",
                rqa.AnyValue,
                doc="",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.logo_default = maybe_from_nullable(self.logo_default)
        self.logo_dark = maybe_from_nullable(self.logo_dark)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "json": to_dict(self.json),
        }
        if self.logo_default.is_just:
            res["logo-default"] = to_dict(self.logo_default.value)
        if self.logo_dark.is_just:
            res["logo-dark"] = to_dict(self.logo_dark.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateTenantData"], d: t.Dict[str, t.Any]
    ) -> "CreateTenantData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            json=parsed.json,
            logo_default=getattr(parsed, "logo-default"),
            logo_dark=getattr(parsed, "logo-dark"),
        )
        res.raw_data = d
        return res
