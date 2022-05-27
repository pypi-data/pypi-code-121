"""The module that defines the ``ExtendedCourseRegistrationLink`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course import Course
from .course_registration_link import CourseRegistrationLink


@dataclass
class ExtendedCourseRegistrationLink(CourseRegistrationLink):
    """The extended variant of a course registration link."""

    #: The course this link will enroll users in
    course: "Course"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: CourseRegistrationLink.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "course",
                    parsers.ParserFor.make(Course),
                    doc="The course this link will enroll users in",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "course": to_dict(self.course),
            "id": to_dict(self.id),
            "expiration_date": to_dict(self.expiration_date),
            "role": to_dict(self.role),
            "allow_register": to_dict(self.allow_register),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedCourseRegistrationLink"], d: t.Dict[str, t.Any]
    ) -> "ExtendedCourseRegistrationLink":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            course=parsed.course,
            id=parsed.id,
            expiration_date=parsed.expiration_date,
            role=parsed.role,
            allow_register=parsed.allow_register,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .course_role import CourseRole

    # fmt: on
