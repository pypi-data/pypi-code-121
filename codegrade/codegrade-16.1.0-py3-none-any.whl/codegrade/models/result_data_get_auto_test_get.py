"""The module that defines the ``ResultDataGetAutoTestGet`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_fixture import AutoTestFixture
from .auto_test_global_setup_script import AutoTestGlobalSetupScript
from .auto_test_set import AutoTestSet
from .extended_auto_test_run import ExtendedAutoTestRun


@dataclass
class ResultDataGetAutoTestGet:
    """An AutoTest as JSON."""

    #: This id of this AutoTest
    id: "int"
    #: The fixtures connected to this AutoTest
    fixtures: "t.Sequence[AutoTestFixture]"
    #: The user provided setup script that will be executed before any test
    #: starts. Deprected, use `global_setup`.
    run_setup_script: "str"
    #: The global setup that will be executed. This are multiple commands that
    #: will be executed in the order of the list.
    global_setup: "t.Sequence[AutoTestGlobalSetupScript]"
    #: The setup script that will be executed for each student. In this script
    #: the submission of the student is available.
    setup_script: "str"
    #: Unused
    finalize_script: "str"
    #: The way the grade is calculated in this AutoTest. This is `null` if the
    #: option is still unset. The value `full` means that to achieve the second
    #: item of a rubric with 4 items 50% or more of the of the points are
    #: needed, while with `partial` more than 25% of the points is enough.
    grade_calculation: "t.Optional[t.Literal['full', 'partial']]"
    #: The sets in this AutoTest. In the UI these are called levels.
    sets: "t.Sequence[AutoTestSet]"
    #: The id of the assignment to which this AutoTest belongs.
    assignment_id: "int"
    #: The runs done with this AutoTest. This is list is always of length 0 or
    #: 1
    runs: "t.Sequence[ExtendedAutoTestRun]"
    #: If `true` the results are visible for students before the deadline. This
    #: is also called "continuous feedback mode". This is `null` if the options
    #: is still unset.
    results_always_visible: "t.Optional[bool]"
    #: If `true` the teacher revision will be used for testing if it is
    #: available for a student. This is `null` if the options is still unset.
    prefer_teacher_revision: "t.Optional[bool]"
    #: If `true` the output of the global setup script wil be cached.
    enable_caching: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="This id of this AutoTest",
            ),
            rqa.RequiredArgument(
                "fixtures",
                rqa.List(parsers.ParserFor.make(AutoTestFixture)),
                doc="The fixtures connected to this AutoTest",
            ),
            rqa.RequiredArgument(
                "run_setup_script",
                rqa.SimpleValue.str,
                doc=(
                    "The user provided setup script that will be executed"
                    " before any test starts. Deprected, use `global_setup`."
                ),
            ),
            rqa.RequiredArgument(
                "global_setup",
                rqa.List(parsers.ParserFor.make(AutoTestGlobalSetupScript)),
                doc=(
                    "The global setup that will be executed. This are multiple"
                    " commands that will be executed in the order of the list."
                ),
            ),
            rqa.RequiredArgument(
                "setup_script",
                rqa.SimpleValue.str,
                doc=(
                    "The setup script that will be executed for each student."
                    " In this script the submission of the student is"
                    " available."
                ),
            ),
            rqa.RequiredArgument(
                "finalize_script",
                rqa.SimpleValue.str,
                doc="Unused",
            ),
            rqa.RequiredArgument(
                "grade_calculation",
                rqa.Nullable(rqa.StringEnum("full", "partial")),
                doc=(
                    "The way the grade is calculated in this AutoTest. This is"
                    " `null` if the option is still unset. The value `full`"
                    " means that to achieve the second item of a rubric with 4"
                    " items 50% or more of the of the points are needed, while"
                    " with `partial` more than 25% of the points is enough."
                ),
            ),
            rqa.RequiredArgument(
                "sets",
                rqa.List(parsers.ParserFor.make(AutoTestSet)),
                doc=(
                    "The sets in this AutoTest. In the UI these are called"
                    " levels."
                ),
            ),
            rqa.RequiredArgument(
                "assignment_id",
                rqa.SimpleValue.int,
                doc="The id of the assignment to which this AutoTest belongs.",
            ),
            rqa.RequiredArgument(
                "runs",
                rqa.List(parsers.ParserFor.make(ExtendedAutoTestRun)),
                doc=(
                    "The runs done with this AutoTest. This is list is always"
                    " of length 0 or 1"
                ),
            ),
            rqa.RequiredArgument(
                "results_always_visible",
                rqa.Nullable(rqa.SimpleValue.bool),
                doc=(
                    "If `true` the results are visible for students before the"
                    ' deadline. This is also called "continuous feedback'
                    ' mode". This is `null` if the options is still unset.'
                ),
            ),
            rqa.RequiredArgument(
                "prefer_teacher_revision",
                rqa.Nullable(rqa.SimpleValue.bool),
                doc=(
                    "If `true` the teacher revision will be used for testing"
                    " if it is available for a student. This is `null` if the"
                    " options is still unset."
                ),
            ),
            rqa.RequiredArgument(
                "enable_caching",
                rqa.SimpleValue.bool,
                doc=(
                    "If `true` the output of the global setup script wil be"
                    " cached."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "fixtures": to_dict(self.fixtures),
            "run_setup_script": to_dict(self.run_setup_script),
            "global_setup": to_dict(self.global_setup),
            "setup_script": to_dict(self.setup_script),
            "finalize_script": to_dict(self.finalize_script),
            "grade_calculation": to_dict(self.grade_calculation),
            "sets": to_dict(self.sets),
            "assignment_id": to_dict(self.assignment_id),
            "runs": to_dict(self.runs),
            "results_always_visible": to_dict(self.results_always_visible),
            "prefer_teacher_revision": to_dict(self.prefer_teacher_revision),
            "enable_caching": to_dict(self.enable_caching),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ResultDataGetAutoTestGet"], d: t.Dict[str, t.Any]
    ) -> "ResultDataGetAutoTestGet":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            fixtures=parsed.fixtures,
            run_setup_script=parsed.run_setup_script,
            global_setup=parsed.global_setup,
            setup_script=parsed.setup_script,
            finalize_script=parsed.finalize_script,
            grade_calculation=parsed.grade_calculation,
            sets=parsed.sets,
            assignment_id=parsed.assignment_id,
            runs=parsed.runs,
            results_always_visible=parsed.results_always_visible,
            prefer_teacher_revision=parsed.prefer_teacher_revision,
            enable_caching=parsed.enable_caching,
        )
        res.raw_data = d
        return res
