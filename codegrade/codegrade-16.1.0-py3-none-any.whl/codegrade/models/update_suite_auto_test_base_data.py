"""The module that defines the ``UpdateSuiteAutoTestBaseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .check_points_input_as_json import CheckPointsInputAsJSON
from .code_quality_input_as_json import CodeQualityInputAsJSON
from .custom_output_input_as_json import CustomOutputInputAsJSON
from .io_test_input_as_json import IOTestInputAsJSON
from .junit_test_input_as_json import JunitTestInputAsJSON
from .run_program_input_as_json import RunProgramInputAsJSON


@dataclass
class UpdateSuiteAutoTestBaseData:
    """The required data for the AutoTest::UpdateSuite operation."""

    #: The steps that should be in this suite. They will be run as the order
    #: they are provided in.
    steps: "t.Sequence[t.Union[IOTestInputAsJSON, RunProgramInputAsJSON, CustomOutputInputAsJSON, CheckPointsInputAsJSON, JunitTestInputAsJSON, CodeQualityInputAsJSON]]"
    #: The id of the rubric row that should be connected to this suite.
    rubric_row_id: "int"
    #: Should the network be disabled when running steps in this suite
    network_disabled: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "steps",
                rqa.List(
                    parsers.make_union(
                        parsers.ParserFor.make(IOTestInputAsJSON),
                        parsers.ParserFor.make(RunProgramInputAsJSON),
                        parsers.ParserFor.make(CustomOutputInputAsJSON),
                        parsers.ParserFor.make(CheckPointsInputAsJSON),
                        parsers.ParserFor.make(JunitTestInputAsJSON),
                        parsers.ParserFor.make(CodeQualityInputAsJSON),
                    )
                ),
                doc=(
                    "The steps that should be in this suite. They will be run"
                    " as the order they are provided in."
                ),
            ),
            rqa.RequiredArgument(
                "rubric_row_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the rubric row that should be connected to this"
                    " suite."
                ),
            ),
            rqa.RequiredArgument(
                "network_disabled",
                rqa.SimpleValue.bool,
                doc=(
                    "Should the network be disabled when running steps in this"
                    " suite"
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "steps": to_dict(self.steps),
            "rubric_row_id": to_dict(self.rubric_row_id),
            "network_disabled": to_dict(self.network_disabled),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UpdateSuiteAutoTestBaseData"], d: t.Dict[str, t.Any]
    ) -> "UpdateSuiteAutoTestBaseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            steps=parsed.steps,
            rubric_row_id=parsed.rubric_row_id,
            network_disabled=parsed.network_disabled,
        )
        res.raw_data = d
        return res
