"""The module that defines the ``CourseStatisticsAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CourseStatisticsAsJSON:
    """Information about the amount of active students a course has."""

    #: The amount of "active" students this course has. An active student is a
    #: a student that has created a submission within the last 31 days.
    active_student_amount: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "active_student_amount",
                rqa.SimpleValue.int,
                doc=(
                    'The amount of "active" students this course has. An'
                    " active student is a a student that has created a"
                    " submission within the last 31 days."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "active_student_amount": to_dict(self.active_student_amount),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CourseStatisticsAsJSON"], d: t.Dict[str, t.Any]
    ) -> "CourseStatisticsAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            active_student_amount=parsed.active_student_amount,
        )
        res.raw_data = d
        return res
