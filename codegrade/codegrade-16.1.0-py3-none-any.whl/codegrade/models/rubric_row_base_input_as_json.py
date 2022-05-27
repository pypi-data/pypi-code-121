"""The module that defines the ``RubricRowBaseInputAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .rubric_row_base_input_base_as_json import RubricRowBaseInputBaseAsJSON


@dataclass
class RubricRowBaseInputAsJSON(RubricRowBaseInputBaseAsJSON):
    """The JSON needed to update a rubric row."""

    #: The id, pass this to update an existing row, omit it to create a new
    #: row.
    id: Maybe["int"] = Nothing
    #: The type of rubric row. Will default to "normal" if not passed.
    type: Maybe["str"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: RubricRowBaseInputBaseAsJSON.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "id",
                    rqa.SimpleValue.int,
                    doc=(
                        "The id, pass this to update an existing row, omit it"
                        " to create a new row."
                    ),
                ),
                rqa.OptionalArgument(
                    "type",
                    rqa.SimpleValue.str,
                    doc=(
                        'The type of rubric row. Will default to "normal" if'
                        " not passed."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.id = maybe_from_nullable(self.id)
        self.type = maybe_from_nullable(self.type)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "header": to_dict(self.header),
            "description": to_dict(self.description),
            "items": to_dict(self.items),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        if self.type.is_just:
            res["type"] = to_dict(self.type.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RubricRowBaseInputAsJSON"], d: t.Dict[str, t.Any]
    ) -> "RubricRowBaseInputAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            header=parsed.header,
            description=parsed.description,
            items=parsed.items,
            id=parsed.id,
            type=parsed.type,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .rubric_item_input_as_json import RubricItemInputAsJSON

    # fmt: on
