"""The module that defines the ``UpdateSuiteAutoTestData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .update_suite_auto_test_base_data import UpdateSuiteAutoTestBaseData


@dataclass
class UpdateSuiteAutoTestData(UpdateSuiteAutoTestBaseData):
    """The required and optional data for the AutoTest::UpdateSuite operation."""

    #: The id of the suite you want to edit. If not provided we will create a
    #: new suite.
    id: Maybe["int"] = Nothing
    #: If passed as `true` we will provide information about the current
    #: submission while running steps. Defaults to `false` when creating new
    #: suites.
    submission_info: Maybe["bool"] = Nothing
    #: The maximum amount of time a single step (or substeps) can take when
    #: running tests. If not provided the default value is depended on
    #: configuration of the instance.
    command_time_limit: Maybe["datetime.timedelta"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: UpdateSuiteAutoTestBaseData.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "id",
                    rqa.SimpleValue.int,
                    doc=(
                        "The id of the suite you want to edit. If not provided"
                        " we will create a new suite."
                    ),
                ),
                rqa.OptionalArgument(
                    "submission_info",
                    rqa.SimpleValue.bool,
                    doc=(
                        "If passed as `true` we will provide information about"
                        " the current submission while running steps. Defaults"
                        " to `false` when creating new suites."
                    ),
                ),
                rqa.OptionalArgument(
                    "command_time_limit",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The maximum amount of time a single step (or"
                        " substeps) can take when running tests. If not"
                        " provided the default value is depended on"
                        " configuration of the instance."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.id = maybe_from_nullable(self.id)
        self.submission_info = maybe_from_nullable(self.submission_info)
        self.command_time_limit = maybe_from_nullable(self.command_time_limit)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "steps": to_dict(self.steps),
            "rubric_row_id": to_dict(self.rubric_row_id),
            "network_disabled": to_dict(self.network_disabled),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        if self.submission_info.is_just:
            res["submission_info"] = to_dict(self.submission_info.value)
        if self.command_time_limit.is_just:
            res["command_time_limit"] = to_dict(self.command_time_limit.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UpdateSuiteAutoTestData"], d: t.Dict[str, t.Any]
    ) -> "UpdateSuiteAutoTestData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            steps=parsed.steps,
            rubric_row_id=parsed.rubric_row_id,
            network_disabled=parsed.network_disabled,
            id=parsed.id,
            submission_info=parsed.submission_info,
            command_time_limit=parsed.command_time_limit,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .check_points_input_as_json import CheckPointsInputAsJSON
    from .code_quality_input_as_json import CodeQualityInputAsJSON
    from .custom_output_input_as_json import CustomOutputInputAsJSON
    from .io_test_input_as_json import IOTestInputAsJSON
    from .junit_test_input_as_json import JunitTestInputAsJSON
    from .run_program_input_as_json import RunProgramInputAsJSON

    # fmt: on
