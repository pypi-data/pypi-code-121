"""The module that defines the ``RubricItem`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_rubric_item import BaseRubricItem


@dataclass
class RubricItem(BaseRubricItem):
    """The JSON representation of a rubric item."""

    #: The id of this rubric item.
    id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseRubricItem.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "id",
                    rqa.SimpleValue.int,
                    doc="The id of this rubric item.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "description": to_dict(self.description),
            "header": to_dict(self.header),
            "points": to_dict(self.points),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RubricItem"], d: t.Dict[str, t.Any]
    ) -> "RubricItem":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            description=parsed.description,
            header=parsed.header,
            points=parsed.points,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
