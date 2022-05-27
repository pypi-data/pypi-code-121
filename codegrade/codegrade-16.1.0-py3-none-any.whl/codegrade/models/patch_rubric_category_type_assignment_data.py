"""The module that defines the ``PatchRubricCategoryTypeAssignmentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .rubric_row_base_input_base_as_json import RubricRowBaseInputBaseAsJSON


@dataclass
class PatchRubricCategoryTypeAssignmentData:
    """Input data required for the `Assignment::PatchRubricCategoryType`
    operation.
    """

    #: The new type of the row. This may not be the same as the existing type.
    new_type: "t.Literal['normal', 'continuous']"
    #: The new items of the row.
    row: "RubricRowBaseInputBaseAsJSON"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "new_type",
                rqa.StringEnum("normal", "continuous"),
                doc=(
                    "The new type of the row. This may not be the same as the"
                    " existing type."
                ),
            ),
            rqa.RequiredArgument(
                "row",
                parsers.ParserFor.make(RubricRowBaseInputBaseAsJSON),
                doc="The new items of the row.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "new_type": to_dict(self.new_type),
            "row": to_dict(self.row),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchRubricCategoryTypeAssignmentData"],
        d: t.Dict[str, t.Any],
    ) -> "PatchRubricCategoryTypeAssignmentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            new_type=parsed.new_type,
            row=parsed.row,
        )
        res.raw_data = d
        return res
