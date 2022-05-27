"""The module that defines the ``AutoTestStepBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .any_redacted_auto_test_step_as_json import AnyRedactedAutoTestStepAsJSON
from .check_points_as_json import CheckPointsAsJSON
from .code_quality_as_json import CodeQualityAsJSON
from .custom_output_as_json import CustomOutputAsJSON
from .io_test_as_json import IOTestAsJSON
from .junit_test_as_json import JunitTestAsJSON
from .run_program_as_json import RunProgramAsJSON

AutoTestStepBase_1 = t.Union[
    IOTestAsJSON,
    RunProgramAsJSON,
    CustomOutputAsJSON,
    CheckPointsAsJSON,
    JunitTestAsJSON,
    CodeQualityAsJSON,
]
AutoTestStepBase_1Parser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(IOTestAsJSON),
        ParserFor.make(RunProgramAsJSON),
        ParserFor.make(CustomOutputAsJSON),
        ParserFor.make(CheckPointsAsJSON),
        ParserFor.make(JunitTestAsJSON),
        ParserFor.make(CodeQualityAsJSON),
    ),
)

AutoTestStepBase = t.Union[
    AutoTestStepBase_1,
    AnyRedactedAutoTestStepAsJSON,
]
AutoTestStepBaseParser = rqa.Lazy(
    lambda: make_union(
        AutoTestStepBase_1Parser, ParserFor.make(AnyRedactedAutoTestStepAsJSON)
    ),
)
