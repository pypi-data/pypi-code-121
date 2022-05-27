"""The module that defines the ``IOTestStepLogBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_step_result_state import AutoTestStepResultState


@dataclass
class IOTestStepLogBase:
    """The base data for a single IO test step."""

    #: The state of this step.
    state: "AutoTestStepResultState"
    #: The moment the step result was created.
    created_at: "datetime.datetime"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(AutoTestStepResultState),
                doc="The state of this step.",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment the step result was created.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "state": to_dict(self.state),
            "created_at": to_dict(self.created_at),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestStepLogBase"], d: t.Dict[str, t.Any]
    ) -> "IOTestStepLogBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            state=parsed.state,
            created_at=parsed.created_at,
        )
        res.raw_data = d
        return res
