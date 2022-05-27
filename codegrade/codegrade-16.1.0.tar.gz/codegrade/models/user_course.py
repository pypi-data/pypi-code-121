"""The module that defines the ``UserCourse`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_role import CourseRole
from .user import User


@dataclass
class UserCourse:
    """A user and their role in a course."""

    #: The user.
    user: "User"
    #: The role they have in the course.
    course_role: "CourseRole"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "User",
                parsers.ParserFor.make(User),
                doc="The user.",
            ),
            rqa.RequiredArgument(
                "CourseRole",
                parsers.ParserFor.make(CourseRole),
                doc="The role they have in the course.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "User": to_dict(self.user),
            "CourseRole": to_dict(self.course_role),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UserCourse"], d: t.Dict[str, t.Any]
    ) -> "UserCourse":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            user=parsed.User,
            course_role=parsed.CourseRole,
        )
        res.raw_data = d
        return res
