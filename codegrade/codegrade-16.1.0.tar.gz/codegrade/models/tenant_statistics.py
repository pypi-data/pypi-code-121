"""The module that defines the ``TenantStatistics`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .tenant_course_statistics import TenantCourseStatistics


@dataclass
class TenantStatistics:
    """Various statistics that describe the tenant."""

    #: The amount of students. This will be a mapping from academic to the
    #: amount of students. The end year of the academic year is used, so the
    #: amount of students for 2020/2021 academic year can be found under the
    #: key `2021`.
    student_amounts: "t.Mapping[str, int]"
    #: The amount of submissions handed-in to courses of this tenant in the
    #: last week.
    amount_submissions_last_week: "int"
    #: Information about the amount of courses.
    course_amounts: "TenantCourseStatistics"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "student_amounts",
                rqa.LookupMapping(rqa.SimpleValue.int),
                doc=(
                    "The amount of students. This will be a mapping from"
                    " academic to the amount of students. The end year of the"
                    " academic year is used, so the amount of students for"
                    " 2020/2021 academic year can be found under the key"
                    " `2021`."
                ),
            ),
            rqa.RequiredArgument(
                "amount_submissions_last_week",
                rqa.SimpleValue.int,
                doc=(
                    "The amount of submissions handed-in to courses of this"
                    " tenant in the last week."
                ),
            ),
            rqa.RequiredArgument(
                "course_amounts",
                parsers.ParserFor.make(TenantCourseStatistics),
                doc="Information about the amount of courses.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "student_amounts": to_dict(self.student_amounts),
            "amount_submissions_last_week": to_dict(
                self.amount_submissions_last_week
            ),
            "course_amounts": to_dict(self.course_amounts),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["TenantStatistics"], d: t.Dict[str, t.Any]
    ) -> "TenantStatistics":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            student_amounts=parsed.student_amounts,
            amount_submissions_last_week=parsed.amount_submissions_last_week,
            course_amounts=parsed.course_amounts,
        )
        res.raw_data = d
        return res
