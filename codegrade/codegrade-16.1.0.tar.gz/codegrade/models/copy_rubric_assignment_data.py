"""The module that defines the ``CopyRubricAssignmentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CopyRubricAssignmentData:
    """Input data required for the `Assignment::CopyRubric` operation."""

    #: The id of the assignment from which you want to copy the rubric.
    old_assignment_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "old_assignment_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the assignment from which you want to copy the"
                    " rubric."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "old_assignment_id": to_dict(self.old_assignment_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CopyRubricAssignmentData"], d: t.Dict[str, t.Any]
    ) -> "CopyRubricAssignmentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            old_assignment_id=parsed.old_assignment_id,
        )
        res.raw_data = d
        return res
