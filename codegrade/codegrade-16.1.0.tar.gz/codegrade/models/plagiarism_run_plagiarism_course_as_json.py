"""The module that defines the ``PlagiarismRunPlagiarismCourseAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PlagiarismRunPlagiarismCourseAsJSON:
    """This object represents an course that is connected to a plagiarism run
    or case.
    """

    #: The id of the course
    id: "int"
    #: The name of the course.
    name: "str"
    #: Is this is a virtual course?
    virtual: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the course",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the course.",
            ),
            rqa.RequiredArgument(
                "virtual",
                rqa.SimpleValue.bool,
                doc="Is this is a virtual course?",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "virtual": to_dict(self.virtual),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PlagiarismRunPlagiarismCourseAsJSON"],
        d: t.Dict[str, t.Any],
    ) -> "PlagiarismRunPlagiarismCourseAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            name=parsed.name,
            virtual=parsed.virtual,
        )
        res.raw_data = d
        return res
