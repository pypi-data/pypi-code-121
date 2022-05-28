import os

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import _pytest
import pluggy

from _pytest._code.code import ExceptionInfo
from cleo.formatters.formatter import Formatter
from cleo.io.outputs.output import Output
from cleo.io.outputs.section_output import SectionOutput

import treat

from treat.ui.exception_trace import ExceptionTrace

from .state import State
from .test_report import TestReport
from .test_result import TestResult


class Style:

    _TYPES = [TestResult.PASS, TestResult.FAIL, TestResult.SKIPPED]

    def __init__(self, output: Output) -> None:
        self._output = output
        self._footer: SectionOutput = self._output.section()
        self._ignore_files_in = r"^({}|{}|{}|{})".format(
            os.path.dirname(_pytest.__file__),
            os.path.dirname(pluggy.__file__),
            treat.__file__,
            os.path.join(os.path.dirname(treat.__file__), "mock"),
        )
        self._inline_errors = False
        self._errors: Dict[Tuple[str], List[TestResult]] = {}
        self._errors_count = 0

    @property
    def footer(self) -> SectionOutput:
        return self._footer

    def inline_errors(self, inline_errors: bool = True) -> "Style":
        self._inline_errors = inline_errors

        return self

    def write_current_recap(self, state: State) -> None:
        if not state.group_tests_count:
            return

        self._footer.clear()

        self._output.write_line(
            self._title_line(
                "black", state.group_title_color, state.group_title, state.group
            )
        )

        for test in state.tests:
            description = test.description

            if test.parameters:
                description += " <fg=blue><b>#</b>{}</blue>".format(
                    state.parameter_set(test)
                )

            self._output.write_line(
                self._test_line(
                    test.color,
                    test.icon,
                    description,
                    warning=test.skip_reason if test.is_skipped() else None,
                )
            )
            if self._output.is_very_verbose():
                self._output.write_line("    " + self._identifier_line(test.identifier))

                self._write_parameters(test)

            if test.error:
                self._errors.setdefault(state.group, [])
                self._errors[state.group].append(test)
                self._errors_count += 1

                if self._inline_errors:
                    self._write_error(test)

    def update_footer(self, state: State, report: Optional[TestReport] = None) -> None:
        self._footer.overwrite(self._footer_content(state, report))

    def write_recap(self, state: State, elapsed: float) -> None:
        self._footer.clear()

        if self._errors and not self._inline_errors:
            self.write_errors_summary()

        self._output.write_line(self._footer_content(state))
        self._output.write_line(
            f"  <fg=default;options=bold>Time:   </><fg=default>{elapsed:0.2f}s</>"
        )

    def write_errors_summary(self) -> None:
        i = 1
        padding = len(str(self._errors_count))
        for group, errors in self._errors.items():
            for test in errors:
                self._output.write_line("")
                if len(self._errors) > 1:
                    self._output.write_line("")
                    line = (
                        f"<fg=red;options=bold>Failing</> test "
                        f"<fg=default;options=dark>(</><fg=default;options=bold>{i:{padding}}<fg=default;options=dark>/</>{self._errors_count}</><fg=default;options=dark>)</>"
                    )
                    self._output.write_line("  <fg=default;options=bold># " + line)
                    self._output.write_line("")

                self._output.write_line(
                    f"  <fg=red;options=bold>• "
                    f"{self._group_line(group)} "
                    f"<fg=default;options=dark>></> "
                    f"<fg=red;options=bold>{test.description}</>"
                    "</>"
                )
                self._output.write_line("    " + self._identifier_line(test.identifier))
                self._write_error(test)
                i += 1

    def _write_error(self, test: TestResult) -> None:
        self._write_parameters(test)

        if test.stdout:
            self._output.write_line("")
            self._output.write_line("    <fg=default;options=bold>Stdout:</>")
            self._output.write_line("")
            self._output.write_line(
                "    "
                + self._output.formatter.escape(test.stdout).replace("\n", "\n    ")
            )

        error = test.error
        if isinstance(error, ExceptionInfo):
            error = error.value

        trace = ExceptionTrace(error, base_indent=2)
        trace.ignore_files_in(self._ignore_files_in)
        trace.render(self._output)

        self._output.write_line("")

    def _type_color(self, type: str) -> str:
        if type == TestResult.FAIL:
            return "red"
        elif type == TestResult.SKIPPED:
            return "yellow"

        return "green"

    def _title_line(self, fg: str, bg: str, title: str, group: Tuple[str]) -> str:
        group = self._group_line(group)

        return f"\n  <fg={bg};options=bold>{title}</> <fg=default;options=dark,bold>•</> {group}"

    def _group_line(self, group: Tuple[str]) -> str:
        path = group[0]
        path_parts = path.split(os.path.sep)
        for i, part in enumerate(path_parts[:-1]):
            path_parts[i] = f"<fg=default>{part}</>"

        path_parts[-1] = f"<fg=default;options=bold>{path_parts[-1]}</>"
        line = f"<fg=default;options=dark>{os.path.sep}</>".join(path_parts)

        if len(group) > 1:
            line += " <fg=default;options=dark>></> "
            line += f"<fg=default;options=bold>{group[1]}</>"
            line += " <fg=default;options=dark>></> ".join(
                f"<fg=default;options=bold>{g}" for g in group[1:-1]
            )

        return line

    def _test_line(
        self,
        fg: str,
        icon: str,
        description: str,
        warning: Optional[str] = None,
    ) -> str:
        if warning:
            warning = (
                f" <fg=default;options=dark>(<fg=default;options=bold>Skipped</>: "
                f"<fg=yellow;options=bold>{warning}</>)</>"
            )
        else:
            warning = ""

        return (
            f"  <fg={fg};options=bold>{icon}</><fg=default> {description}{warning}</>"
        )

    def _identifier_line(self, identifier: str) -> str:
        return f"<fg=default;options=dark>{identifier}</>"

    def _footer_content(self, state: State, report: Optional[TestReport] = None) -> str:
        runs = []

        if report:
            runs.append(self._title_line("black", "blue", "RUNS", state.group))

            test = TestResult.create_from_test_report(report)
            description = test.description
            if test.parameters:
                description += " <fg=blue><b>#</b>{}</blue>".format(
                    state.parameter_set(test)
                )

            runs.append(self._test_line(test.color, test.icon, description))

        tests = []
        for type in self._TYPES:
            tests_count = state.count_tests_in_suite_with_type(type)
            if tests_count:
                color = self._type_color(type)
                tests.append(
                    f"<fg={color}><fg={color};option=bold>{tests_count}</> {type}</>"
                )

        pending = state.suite_total_tests - state.suite_tests_count
        if pending:
            tests.append(
                f"<fg=default;options=dark><fg=default;options=dark,bold>{pending}</> pending</>"
            )

        if tests:
            footer = "\n".join(
                runs
                + [""]
                + [
                    f"  <fg=default;options=bold>Tests:  </><fg=default>{', '.join(tests)}</>"
                ]
            )

            return footer

        return ""

    def _write_parameters(self, test: TestResult) -> None:
        if not test.parameters:
            return

        self._output.write_line("")
        for name, value in test.parameters:
            color = "default"
            if isinstance(value, (int, float)):
                color = "blue"
            elif isinstance(value, (str, bytes)):
                color = "yellow"

            param_description = (
                f"    <fg=default;option=bold>{name}</><fg=default;options=dark>:</> "
            )
            param_description += f"<fg={color}>{Formatter.escape(repr(value))}</>"
            self._output.write_line(param_description)

        self._output.write_line("")
