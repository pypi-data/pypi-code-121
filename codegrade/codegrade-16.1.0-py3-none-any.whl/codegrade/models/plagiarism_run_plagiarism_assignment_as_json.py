"""The module that defines the ``PlagiarismRunPlagiarismAssignmentAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PlagiarismRunPlagiarismAssignmentAsJSON:
    """This object represents an assignment that is connected to a plagiarism
    run or case.
    """

    #: The id of the assignment.
    id: "int"
    #: The name of the assignment
    name: "str"
    #: The id of the course the assignment is in.
    course_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the assignment.",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the assignment",
            ),
            rqa.RequiredArgument(
                "course_id",
                rqa.SimpleValue.int,
                doc="The id of the course the assignment is in.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "course_id": to_dict(self.course_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PlagiarismRunPlagiarismAssignmentAsJSON"],
        d: t.Dict[str, t.Any],
    ) -> "PlagiarismRunPlagiarismAssignmentAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            name=parsed.name,
            course_id=parsed.course_id,
        )
        res.raw_data = d
        return res
