"""The module that defines the ``AutoTestFixture`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_file import BaseFile


@dataclass
class AutoTestFixture(BaseFile):
    """The fixture as JSON."""

    #: Is this fixture hidden.
    hidden: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseFile.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "hidden",
                    rqa.SimpleValue.bool,
                    doc="Is this fixture hidden.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "hidden": to_dict(self.hidden),
            "type": to_dict(self.type),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "size": to_dict(self.size),
            "hash": to_dict(self.hash),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestFixture"], d: t.Dict[str, t.Any]
    ) -> "AutoTestFixture":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            hidden=parsed.hidden,
            type=parsed.type,
            id=parsed.id,
            name=parsed.name,
            size=parsed.size,
            hash=parsed.hash,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
