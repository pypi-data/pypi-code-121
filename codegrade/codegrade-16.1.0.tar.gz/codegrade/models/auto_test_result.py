"""The module that defines the ``AutoTestResult`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_result_state import AutoTestResultState


@dataclass
class AutoTestResult:
    """The JSON representation of a result."""

    #: The id of this result
    id: "int"
    #: The time this result was created
    created_at: "datetime.datetime"
    #: The time this result was last updated
    updated_at: "datetime.datetime"
    #: The moment this result was started. If this is `null` the result has not
    #: yet started.
    started_at: "t.Optional[datetime.datetime]"
    #: The id of the submission (work) that was tested in this result.
    work_id: "int"
    #: The state the result is in.
    state: "AutoTestResultState"
    #: The amount of points achieved in this step by the student.
    points_achieved: "float"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of this result",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The time this result was created",
            ),
            rqa.RequiredArgument(
                "updated_at",
                rqa.RichValue.DateTime,
                doc="The time this result was last updated",
            ),
            rqa.RequiredArgument(
                "started_at",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc=(
                    "The moment this result was started. If this is `null` the"
                    " result has not yet started."
                ),
            ),
            rqa.RequiredArgument(
                "work_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the submission (work) that was tested in this"
                    " result."
                ),
            ),
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(AutoTestResultState),
                doc="The state the result is in.",
            ),
            rqa.RequiredArgument(
                "points_achieved",
                rqa.SimpleValue.float,
                doc=(
                    "The amount of points achieved in this step by the"
                    " student."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
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
        cls: t.Type["AutoTestResult"], d: t.Dict[str, t.Any]
    ) -> "AutoTestResult":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
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
