"""The module that defines the ``RubricItemInputAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .base_rubric_item import BaseRubricItem


@dataclass
class RubricItemInputAsJSON(BaseRubricItem):
    """The JSON needed to update a rubric item."""

    #: The id of this rubric item. Pass this to update an existing rubric item,
    #: omit if you want to create a new item.
    id: Maybe["int"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseRubricItem.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "id",
                    rqa.SimpleValue.int,
                    doc=(
                        "The id of this rubric item. Pass this to update an"
                        " existing rubric item, omit if you want to create a"
                        " new item."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.id = maybe_from_nullable(self.id)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "description": to_dict(self.description),
            "header": to_dict(self.header),
            "points": to_dict(self.points),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RubricItemInputAsJSON"], d: t.Dict[str, t.Any]
    ) -> "RubricItemInputAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            description=parsed.description,
            header=parsed.header,
            points=parsed.points,
            id=parsed.id,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
