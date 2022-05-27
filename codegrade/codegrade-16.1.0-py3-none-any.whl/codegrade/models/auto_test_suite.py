"""The module that defines the ``AutoTestSuite`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_step_base import AutoTestStepBase, AutoTestStepBaseParser
from .rubric_row_base import RubricRowBase


@dataclass
class AutoTestSuite:
    """The set as JSON."""

    #: The id of this suite (or "category")
    id: "int"
    #: The steps that will be executed in this suite.
    steps: "t.Sequence[AutoTestStepBase]"
    #: The rubric row this category is connected to.
    rubric_row: "RubricRowBase"
    #: Is the network disabled while running this category.
    network_disabled: "bool"
    #: Will submission info be available while running this step.
    submission_info: "bool"
    #: The maximum amount of time a step (or substep) may take. If `null` the
    #: instance default will be used.
    command_time_limit: "t.Optional[datetime.timedelta]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc='The id of this suite (or "category")',
            ),
            rqa.RequiredArgument(
                "steps",
                rqa.List(AutoTestStepBaseParser),
                doc="The steps that will be executed in this suite.",
            ),
            rqa.RequiredArgument(
                "rubric_row",
                parsers.ParserFor.make(RubricRowBase),
                doc="The rubric row this category is connected to.",
            ),
            rqa.RequiredArgument(
                "network_disabled",
                rqa.SimpleValue.bool,
                doc="Is the network disabled while running this category.",
            ),
            rqa.RequiredArgument(
                "submission_info",
                rqa.SimpleValue.bool,
                doc=(
                    "Will submission info be available while running this"
                    " step."
                ),
            ),
            rqa.RequiredArgument(
                "command_time_limit",
                rqa.Nullable(rqa.RichValue.TimeDelta),
                doc=(
                    "The maximum amount of time a step (or substep) may take."
                    " If `null` the instance default will be used."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "steps": to_dict(self.steps),
            "rubric_row": to_dict(self.rubric_row),
            "network_disabled": to_dict(self.network_disabled),
            "submission_info": to_dict(self.submission_info),
            "command_time_limit": to_dict(self.command_time_limit),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestSuite"], d: t.Dict[str, t.Any]
    ) -> "AutoTestSuite":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            steps=parsed.steps,
            rubric_row=parsed.rubric_row,
            network_disabled=parsed.network_disabled,
            submission_info=parsed.submission_info,
            command_time_limit=parsed.command_time_limit,
        )
        res.raw_data = d
        return res
