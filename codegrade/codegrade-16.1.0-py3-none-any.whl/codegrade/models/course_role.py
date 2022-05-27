"""The module that defines the ``CourseRole`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .abstract_role import AbstractRole
from .course import Course


@dataclass
class CourseRole(AbstractRole):
    """The JSON representation of a course role."""

    #: The course this role is connected to
    course: "Course"
    #: Is this role hidden
    hidden: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AbstractRole.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "course",
                    parsers.ParserFor.make(Course),
                    doc="The course this role is connected to",
                ),
                rqa.RequiredArgument(
                    "hidden",
                    rqa.SimpleValue.bool,
                    doc="Is this role hidden",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "course": to_dict(self.course),
            "hidden": to_dict(self.hidden),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CourseRole"], d: t.Dict[str, t.Any]
    ) -> "CourseRole":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            course=parsed.course,
            hidden=parsed.hidden,
            id=parsed.id,
            name=parsed.name,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
