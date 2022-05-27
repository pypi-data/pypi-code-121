"""The module that defines the ``IOTestStepLog`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .io_test_step_log_base import IOTestStepLogBase


@dataclass
class IOTestStepLog(IOTestStepLogBase):
    """The data for a single IO test step."""

    #: The stdout produced by this step.
    stdout: Maybe["str"] = Nothing
    #: The stderr produced by this step.
    stderr: Maybe["str"] = Nothing
    #: The exit code of the step
    exit_code: Maybe["int"] = Nothing
    #: The time spend while running the step
    time_spend: Maybe["datetime.timedelta"] = Nothing
    #: The moment the step was started, if it has already been started.
    started_at: Maybe["t.Optional[datetime.datetime]"] = Nothing
    #: The amount of points achieved in this step.
    achieved_points: Maybe["float"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: IOTestStepLogBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "stdout",
                    rqa.SimpleValue.str,
                    doc="The stdout produced by this step.",
                ),
                rqa.OptionalArgument(
                    "stderr",
                    rqa.SimpleValue.str,
                    doc="The stderr produced by this step.",
                ),
                rqa.OptionalArgument(
                    "exit_code",
                    rqa.SimpleValue.int,
                    doc="The exit code of the step",
                ),
                rqa.OptionalArgument(
                    "time_spend",
                    rqa.RichValue.TimeDelta,
                    doc="The time spend while running the step",
                ),
                rqa.OptionalArgument(
                    "started_at",
                    rqa.Nullable(rqa.RichValue.DateTime),
                    doc=(
                        "The moment the step was started, if it has already"
                        " been started."
                    ),
                ),
                rqa.OptionalArgument(
                    "achieved_points",
                    rqa.SimpleValue.float,
                    doc="The amount of points achieved in this step.",
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.stdout = maybe_from_nullable(self.stdout)
        self.stderr = maybe_from_nullable(self.stderr)
        self.exit_code = maybe_from_nullable(self.exit_code)
        self.time_spend = maybe_from_nullable(self.time_spend)
        self.started_at = maybe_from_nullable(self.started_at)
        self.achieved_points = maybe_from_nullable(self.achieved_points)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "state": to_dict(self.state),
            "created_at": to_dict(self.created_at),
        }
        if self.stdout.is_just:
            res["stdout"] = to_dict(self.stdout.value)
        if self.stderr.is_just:
            res["stderr"] = to_dict(self.stderr.value)
        if self.exit_code.is_just:
            res["exit_code"] = to_dict(self.exit_code.value)
        if self.time_spend.is_just:
            res["time_spend"] = to_dict(self.time_spend.value)
        if self.started_at.is_just:
            res["started_at"] = to_dict(self.started_at.value)
        if self.achieved_points.is_just:
            res["achieved_points"] = to_dict(self.achieved_points.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestStepLog"], d: t.Dict[str, t.Any]
    ) -> "IOTestStepLog":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            state=parsed.state,
            created_at=parsed.created_at,
            stdout=parsed.stdout,
            stderr=parsed.stderr,
            exit_code=parsed.exit_code,
            time_spend=parsed.time_spend,
            started_at=parsed.started_at,
            achieved_points=parsed.achieved_points,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .auto_test_step_result_state import AutoTestStepResultState

    # fmt: on
