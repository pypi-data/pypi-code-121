"""The module that defines the ``AutoTestStepResult`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_step_base import AutoTestStepBase, AutoTestStepBaseParser
from .auto_test_step_log_base import AutoTestStepLogBase
from .auto_test_step_result_state import AutoTestStepResultState
from .custom_output_log import CustomOutputLog
from .io_test_log import IOTestLog
from .junit_test_log import JunitTestLog
from .quality_test_log import QualityTestLog
from .run_program_log import RunProgramLog


@dataclass
class AutoTestStepResult:
    """The step result as JSON."""

    #: The id of the result of a step
    id: "int"
    auto_test_step: "AutoTestStepBase"
    #: The state this result is in.
    state: "AutoTestStepResultState"
    #: The amount of points achieved by the student in this step.
    achieved_points: "float"
    #: The log produced by this result. The format of this log depends on the
    #: step result.
    log: "t.Optional[t.Union[CustomOutputLog, JunitTestLog, QualityTestLog, RunProgramLog, IOTestLog, AutoTestStepLogBase]]"
    #: The time this result was started, if `null` the result hasn't started
    #: yet.
    started_at: "t.Optional[datetime.datetime]"
    #: The id of the attachment produced by this result. If `null` no
    #: attachment was produced.
    attachment_id: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the result of a step",
            ),
            rqa.RequiredArgument(
                "auto_test_step",
                AutoTestStepBaseParser,
                doc="",
            ),
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(AutoTestStepResultState),
                doc="The state this result is in.",
            ),
            rqa.RequiredArgument(
                "achieved_points",
                rqa.SimpleValue.float,
                doc=(
                    "The amount of points achieved by the student in this"
                    " step."
                ),
            ),
            rqa.RequiredArgument(
                "log",
                rqa.Nullable(
                    parsers.make_union(
                        parsers.ParserFor.make(CustomOutputLog),
                        parsers.ParserFor.make(JunitTestLog),
                        parsers.ParserFor.make(QualityTestLog),
                        parsers.ParserFor.make(RunProgramLog),
                        parsers.ParserFor.make(IOTestLog),
                        parsers.ParserFor.make(AutoTestStepLogBase),
                    )
                ),
                doc=(
                    "The log produced by this result. The format of this log"
                    " depends on the step result."
                ),
            ),
            rqa.RequiredArgument(
                "started_at",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc=(
                    "The time this result was started, if `null` the result"
                    " hasn't started yet."
                ),
            ),
            rqa.RequiredArgument(
                "attachment_id",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The id of the attachment produced by this result. If"
                    " `null` no attachment was produced."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "auto_test_step": to_dict(self.auto_test_step),
            "state": to_dict(self.state),
            "achieved_points": to_dict(self.achieved_points),
            "log": to_dict(self.log),
            "started_at": to_dict(self.started_at),
            "attachment_id": to_dict(self.attachment_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestStepResult"], d: t.Dict[str, t.Any]
    ) -> "AutoTestStepResult":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            auto_test_step=parsed.auto_test_step,
            state=parsed.state,
            achieved_points=parsed.achieved_points,
            log=parsed.log,
            started_at=parsed.started_at,
            attachment_id=parsed.attachment_id,
        )
        res.raw_data = d
        return res
