"""The module that defines the ``AutoTestRunner`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_runner_state import AutoTestRunnerState


@dataclass
class AutoTestRunner:
    """A runner as JSON."""

    #: The current state of the runner
    state: "AutoTestRunnerState"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(AutoTestRunnerState),
                doc="The current state of the runner",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "state": to_dict(self.state),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestRunner"], d: t.Dict[str, t.Any]
    ) -> "AutoTestRunner":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            state=parsed.state,
        )
        res.raw_data = d
        return res
