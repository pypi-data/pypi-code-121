"""The module that defines the ``IOTestLog`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_step_log_base import AutoTestStepLogBase
from .io_test_step_log import IOTestStepLog


@dataclass
class IOTestLog(AutoTestStepLogBase):
    """The log type of an IO test."""

    #: The log for each step of the io test.
    steps: "t.Sequence[IOTestStepLog]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestStepLogBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "steps",
                    rqa.List(parsers.ParserFor.make(IOTestStepLog)),
                    doc="The log for each step of the io test.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "steps": to_dict(self.steps),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestLog"], d: t.Dict[str, t.Any]
    ) -> "IOTestLog":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            steps=parsed.steps,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
