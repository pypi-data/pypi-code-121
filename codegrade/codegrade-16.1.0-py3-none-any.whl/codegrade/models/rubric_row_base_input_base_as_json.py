"""The module that defines the ``RubricRowBaseInputBaseAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .rubric_item_input_as_json import RubricItemInputAsJSON


@dataclass
class RubricRowBaseInputBaseAsJSON:
    """The required part of the input data for a rubric row."""

    #: The header of this row.
    header: "str"
    #: The description of this row.
    description: "str"
    #: The items in this row.
    items: "t.Sequence[RubricItemInputAsJSON]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "header",
                rqa.SimpleValue.str,
                doc="The header of this row.",
            ),
            rqa.RequiredArgument(
                "description",
                rqa.SimpleValue.str,
                doc="The description of this row.",
            ),
            rqa.RequiredArgument(
                "items",
                rqa.List(parsers.ParserFor.make(RubricItemInputAsJSON)),
                doc="The items in this row.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "header": to_dict(self.header),
            "description": to_dict(self.description),
            "items": to_dict(self.items),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RubricRowBaseInputBaseAsJSON"], d: t.Dict[str, t.Any]
    ) -> "RubricRowBaseInputBaseAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            header=parsed.header,
            description=parsed.description,
            items=parsed.items,
        )
        res.raw_data = d
        return res
