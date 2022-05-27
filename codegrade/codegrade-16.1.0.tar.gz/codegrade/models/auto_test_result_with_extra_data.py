"""The module that defines the ``AutoTestResultWithExtraData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .auto_test_result import AutoTestResult


@dataclass
class AutoTestResultWithExtraData(AutoTestResult):
    """An `AutoTestResults` with an assignment and course id."""

    #: The assignment id of this result.
    assignment_id: "int"
    #: The course id of this result.
    course_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestResult.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "assignment_id",
                    rqa.SimpleValue.int,
                    doc="The assignment id of this result.",
                ),
                rqa.RequiredArgument(
                    "course_id",
                    rqa.SimpleValue.int,
                    doc="The course id of this result.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "assignment_id": to_dict(self.assignment_id),
            "course_id": to_dict(self.course_id),
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "updated_at": to_dict(self.updated_at),
            "started_at": to_dict(self.started_at),
            "work_id": to_dict(self.work_id),
            "state": to_dict(self.state),
            "points_achieved": to_dict(self.points_achieved),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestResultWithExtraData"], d: t.Dict[str, t.Any]
    ) -> "AutoTestResultWithExtraData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            assignment_id=parsed.assignment_id,
            course_id=parsed.course_id,
            id=parsed.id,
            created_at=parsed.created_at,
            updated_at=parsed.updated_at,
            started_at=parsed.started_at,
            work_id=parsed.work_id,
            state=parsed.state,
            points_achieved=parsed.points_achieved,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .auto_test_result_state import AutoTestResultState

    # fmt: on
