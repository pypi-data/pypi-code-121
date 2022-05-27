"""The module that defines the ``ExtendedCourse`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .assignment import Assignment
from .course import Course
from .course_snippet import CourseSnippet
from .group_set import GroupSet


@dataclass
class ExtendedCourse(Course):
    """The way this class will be represented in extended JSON."""

    #: The assignments connected to this assignment.
    assignments: "t.Sequence[Assignment]"
    #: The groups sets of this course.
    group_sets: "t.Sequence[GroupSet]"
    #: The snippets of this course.
    snippets: "t.Sequence[CourseSnippet]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: Course.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "assignments",
                    rqa.List(parsers.ParserFor.make(Assignment)),
                    doc="The assignments connected to this assignment.",
                ),
                rqa.RequiredArgument(
                    "group_sets",
                    rqa.List(parsers.ParserFor.make(GroupSet)),
                    doc="The groups sets of this course.",
                ),
                rqa.RequiredArgument(
                    "snippets",
                    rqa.List(parsers.ParserFor.make(CourseSnippet)),
                    doc="The snippets of this course.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "assignments": to_dict(self.assignments),
            "group_sets": to_dict(self.group_sets),
            "snippets": to_dict(self.snippets),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "created_at": to_dict(self.created_at),
            "virtual": to_dict(self.virtual),
            "lti_provider": to_dict(self.lti_provider),
            "state": to_dict(self.state),
            "tenant_id": to_dict(self.tenant_id),
            "copy_lock_date": to_dict(self.copy_lock_date),
            "price": to_dict(self.price),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedCourse"], d: t.Dict[str, t.Any]
    ) -> "ExtendedCourse":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            assignments=parsed.assignments,
            group_sets=parsed.group_sets,
            snippets=parsed.snippets,
            id=parsed.id,
            name=parsed.name,
            created_at=parsed.created_at,
            virtual=parsed.virtual,
            lti_provider=parsed.lti_provider,
            state=parsed.state,
            tenant_id=parsed.tenant_id,
            copy_lock_date=parsed.copy_lock_date,
            price=parsed.price,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .course_price import CoursePrice
    from .course_state import CourseState
    from .lti_provider_base import LTIProviderBase

    # fmt: on
