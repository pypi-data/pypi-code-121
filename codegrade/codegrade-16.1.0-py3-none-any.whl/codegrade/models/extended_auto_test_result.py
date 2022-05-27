"""The module that defines the ``ExtendedAutoTestResult`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_global_setup_output import AutoTestGlobalSetupOutput
from .auto_test_quality_comment import AutoTestQualityComment
from .auto_test_result import AutoTestResult
from .auto_test_runner import AutoTestRunner
from .auto_test_step_result import AutoTestStepResult
from .file_tree import FileTree, FileTreeParser


@dataclass
class ExtendedAutoTestResult(AutoTestResult):
    """The extended JSON representation of a result."""

    #: The stdout produced in the student setup script. Deprecated use
    #: `global_setup_output`.
    global_setup_stdout: "t.Optional[str]"
    #: The stderr produced in the student setup script. Deprecated use
    #: `global_setup_output`.
    global_setup_stderr: "t.Optional[str]"
    #: The output for the global setup script. As each unit test script can
    #: also cause setup to be produced this is a list of multiple commands and
    #: their output.
    global_setup_output: "t.Sequence[AutoTestGlobalSetupOutput]"
    #: The stdout produced in the student setup script.
    setup_stdout: "t.Optional[str]"
    #: The stderr produced in the student setup script.
    setup_stderr: "t.Optional[str]"
    #: The results for each step in this AutoTest. The ordering of this list is
    #: arbitrary, and the results for entire suites and or sets might be
    #: missing.
    step_results: "t.Sequence[AutoTestStepResult]"
    #: If the result has not started this will contain the amount of students
    #: we expect we still need to run before this result is next. This might be
    #: incorrect and should only be used as a rough estimate.
    approx_waiting_before: "t.Optional[int]"
    #: If `true` this is the final result for the student, meaning that without
    #: teacher interaction (e.g. restarting the AutoTest) this result will not
    #: change and will be used as is to calculate the grade of the student.
    #: Reasons why this may not be the case include but are not limited to the
    #: test containing hidden steps that will only be run after the deadline.
    final_result: "bool"
    #: A mapping between suite id and the files written to the AutoTest output
    #: folder in that suite.
    suite_files: "t.Mapping[str, t.Sequence[FileTree]]"
    #: The quality comments produced by this AutoTest result.
    quality_comments: "t.Sequence[AutoTestQualityComment]"
    #: The runners that could be used to run this result. You can use this to
    #: provide better feedback about the state of a non started result. If the
    #: result is already started this will be `None`.
    possible_runners: "t.Optional[t.Sequence[AutoTestRunner]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestResult.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "global_setup_stdout",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc=(
                        "The stdout produced in the student setup script."
                        " Deprecated use `global_setup_output`."
                    ),
                ),
                rqa.RequiredArgument(
                    "global_setup_stderr",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc=(
                        "The stderr produced in the student setup script."
                        " Deprecated use `global_setup_output`."
                    ),
                ),
                rqa.RequiredArgument(
                    "global_setup_output",
                    rqa.List(
                        parsers.ParserFor.make(AutoTestGlobalSetupOutput)
                    ),
                    doc=(
                        "The output for the global setup script. As each unit"
                        " test script can also cause setup to be produced this"
                        " is a list of multiple commands and their output."
                    ),
                ),
                rqa.RequiredArgument(
                    "setup_stdout",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc="The stdout produced in the student setup script.",
                ),
                rqa.RequiredArgument(
                    "setup_stderr",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc="The stderr produced in the student setup script.",
                ),
                rqa.RequiredArgument(
                    "step_results",
                    rqa.List(parsers.ParserFor.make(AutoTestStepResult)),
                    doc=(
                        "The results for each step in this AutoTest. The"
                        " ordering of this list is arbitrary, and the results"
                        " for entire suites and or sets might be missing."
                    ),
                ),
                rqa.RequiredArgument(
                    "approx_waiting_before",
                    rqa.Nullable(rqa.SimpleValue.int),
                    doc=(
                        "If the result has not started this will contain the"
                        " amount of students we expect we still need to run"
                        " before this result is next. This might be incorrect"
                        " and should only be used as a rough estimate."
                    ),
                ),
                rqa.RequiredArgument(
                    "final_result",
                    rqa.SimpleValue.bool,
                    doc=(
                        "If `true` this is the final result for the student,"
                        " meaning that without teacher interaction (e.g."
                        " restarting the AutoTest) this result will not change"
                        " and will be used as is to calculate the grade of the"
                        " student. Reasons why this may not be the case"
                        " include but are not limited to the test containing"
                        " hidden steps that will only be run after the"
                        " deadline."
                    ),
                ),
                rqa.RequiredArgument(
                    "suite_files",
                    rqa.LookupMapping(rqa.List(FileTreeParser)),
                    doc=(
                        "A mapping between suite id and the files written to"
                        " the AutoTest output folder in that suite."
                    ),
                ),
                rqa.RequiredArgument(
                    "quality_comments",
                    rqa.List(parsers.ParserFor.make(AutoTestQualityComment)),
                    doc=(
                        "The quality comments produced by this AutoTest"
                        " result."
                    ),
                ),
                rqa.RequiredArgument(
                    "possible_runners",
                    rqa.Nullable(
                        rqa.List(parsers.ParserFor.make(AutoTestRunner))
                    ),
                    doc=(
                        "The runners that could be used to run this result."
                        " You can use this to provide better feedback about"
                        " the state of a non started result. If the result is"
                        " already started this will be `None`."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "global_setup_stdout": to_dict(self.global_setup_stdout),
            "global_setup_stderr": to_dict(self.global_setup_stderr),
            "global_setup_output": to_dict(self.global_setup_output),
            "setup_stdout": to_dict(self.setup_stdout),
            "setup_stderr": to_dict(self.setup_stderr),
            "step_results": to_dict(self.step_results),
            "approx_waiting_before": to_dict(self.approx_waiting_before),
            "final_result": to_dict(self.final_result),
            "suite_files": to_dict(self.suite_files),
            "quality_comments": to_dict(self.quality_comments),
            "possible_runners": to_dict(self.possible_runners),
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "updated_at": to_dict(self.updated_at),
            "started_at": to_dict(self.started_at),
            "work_id": to_dict(self.work_id),
            "state": to_dict(self.state),
            "points_achieved": to_dict(self.points_achieved),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedAutoTestResult"], d: t.Dict[str, t.Any]
    ) -> "ExtendedAutoTestResult":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            global_setup_stdout=parsed.global_setup_stdout,
            global_setup_stderr=parsed.global_setup_stderr,
            global_setup_output=parsed.global_setup_output,
            setup_stdout=parsed.setup_stdout,
            setup_stderr=parsed.setup_stderr,
            step_results=parsed.step_results,
            approx_waiting_before=parsed.approx_waiting_before,
            final_result=parsed.final_result,
            suite_files=parsed.suite_files,
            quality_comments=parsed.quality_comments,
            possible_runners=parsed.possible_runners,
            id=parsed.id,
            created_at=parsed.created_at,
            updated_at=parsed.updated_at,
            started_at=parsed.started_at,
            work_id=parsed.work_id,
            state=parsed.state,
            points_achieved=parsed.points_achieved,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .auto_test_result_state import AutoTestResultState

    # fmt: on
