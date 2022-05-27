"""The module that defines the ``QualityTestLogBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .auto_test_step_log_base import AutoTestStepLogBase


@dataclass
class QualityTestLogBase(AutoTestStepLogBase):
    """The log for the QualityTest step type."""

    #: The stdout produced by the step.
    stdout: "str"
    #: The stderr produced by the step.
    stderr: "str"
    #: The exit code of the step.
    exit_code: "int"
    #: The time spend running the step.
    time_spend: "datetime.timedelta"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestStepLogBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "stdout",
                    rqa.SimpleValue.str,
                    doc="The stdout produced by the step.",
                ),
                rqa.RequiredArgument(
                    "stderr",
                    rqa.SimpleValue.str,
                    doc="The stderr produced by the step.",
                ),
                rqa.RequiredArgument(
                    "exit_code",
                    rqa.SimpleValue.int,
                    doc="The exit code of the step.",
                ),
                rqa.RequiredArgument(
                    "time_spend",
                    rqa.RichValue.TimeDelta,
                    doc="The time spend running the step.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "stdout": to_dict(self.stdout),
            "stderr": to_dict(self.stderr),
            "exit_code": to_dict(self.exit_code),
            "time_spend": to_dict(self.time_spend),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["QualityTestLogBase"], d: t.Dict[str, t.Any]
    ) -> "QualityTestLogBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            stdout=parsed.stdout,
            stderr=parsed.stderr,
            exit_code=parsed.exit_code,
            time_spend=parsed.time_spend,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
