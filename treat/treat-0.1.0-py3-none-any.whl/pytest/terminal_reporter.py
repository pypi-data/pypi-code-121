import sys
import time

from io import StringIO
from typing import TYPE_CHECKING
from typing import Optional

import _pytest
import pytest

from _pytest.config import Config
from _pytest.reports import CollectReport
from _pytest.terminal import TerminalReporter as BaseTerminalReporter
from cleo.io.inputs.string_input import StringInput
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from cleo.io.outputs.stream_output import StreamOutput
from cleo.ui.exception_trace import ExceptionTrace

from treat.ui.coverage_reporter import CoverageReporter

from .state import State
from .style import Style
from .test_result import TestResult


if TYPE_CHECKING:
    from treat.ui.coverage_reporter import Coverage


class TerminalReporter(BaseTerminalReporter):

    _VERBOSITY = {
        -1: Verbosity.NORMAL,
        0: Verbosity.VERBOSE,
        1: Verbosity.VERY_VERBOSE,
        2: Verbosity.DEBUG,
        3: Verbosity.DEBUG,
    }

    def __init__(
        self, config: Config, io: Optional[IO] = None, coverage: "Coverage" = None
    ) -> None:
        super(TerminalReporter, self).__init__(config)

        if io is None:
            io = IO(StringInput(""), StreamOutput(sys.stdout), StreamOutput(sys.stderr))

        verbosity = self._VERBOSITY.get(self.verbosity, Verbosity.VERBOSE)
        io.set_verbosity(verbosity)

        # Force pytest to always display full diff on assertion errors
        config.option.verbose = 2

        self._io = io
        self._start_time = time.time()
        self._min_seconds_between_redraws = 0.1
        self._last_write_time = 0
        self._state = State(("___start___",))
        self._style = Style(self._io.output)
        self._style.inline_errors(config.option.maxfail == 1)

        self.isatty = io.is_decorated()
        self._tw.hasmarkup = self.isatty

        self._coverage = coverage

    def pytest_collectreport(self, report: CollectReport) -> None:
        super().pytest_collectreport(report)

        if report.failed:
            trace = ExceptionTrace(report.excinfo.value)
            trace.render(self._io)

    def report_collect(self, final=False) -> None:
        super().report_collect(final=final)

        if final:
            errors = len(self.stats.get("error", []))
            skipped = len(self.stats.get("skipped", []))
            deselected = len(self.stats.get("deselected", []))
            selected = self._numcollected - errors - skipped - deselected

            if self._state.suite_total_tests is None:
                self._state.suite_total_tests = selected

            return

        self._style.footer.overwrite(
            f"\n  <fg=default;options=bold>Tests:  </><fg=default;options=dark><fg=default;options=dark,bold>{self._numcollected}</> pending</>"
        )

    def pytest_sessionstart(self, session):
        # We replace the terminal writer to use a StringIO instance
        # to ensure that pytest does not write something we don't want
        self._tw = _pytest.config.create_terminal_writer(self.config, StringIO())
        self._tw.hasmarkup = self.isatty

        self._session = session
        self._start_time = time.time()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtestloop(self, session):
        yield

        if self._coverage:
            self._coverage.stop()

    def write_fspath_result(self, fspath, res):
        return

    def pytest_runtest_logstart(self, nodeid, location):
        pass

    def pytest_runtest_logreport(self, report):
        test = TestResult.create_from_test_report(report)
        self._state.add_parameter_set_for(test)

        if test.action == "setup":
            if self._state.group_has_changed(test):
                self._style.write_current_recap(self._state)

                self._state.move_to(test)

                self._style.update_footer(self._state, report)
                self._last_write_time = time.time()
            else:
                time_interval = time.time() - self._last_write_time
                if time_interval >= self._min_seconds_between_redraws:
                    self._style.update_footer(self._state, report)
                    self._last_write_time = time.time()

        if test.type in [TestResult.FAIL, TestResult.SKIPPED]:
            self._state.add(test)

        if test.action == "teardown" and not self._state.test_exists_in_group(test):
            self._state.add(
                TestResult.create_from_test_report(report, type=TestResult.PASS)
            )

    def pytest_runtest_logfinish(self, nodeid):
        pass

    def summary_stats(self):
        elapsed = time.time() - self._start_time
        self._style.write_current_recap(self._state)

        self._style.write_recap(self._state, elapsed)

        if self._coverage:
            self._coverage.stop()
            self._coverage.save()

            reporter = CoverageReporter(self._io)
            reporter.render(self._coverage)

    def _update_group_section(self, group):
        tag = "fg=black;bg=blue"
        status = group["status"]
        if status == "fail":
            tag = "fg=black;bg=red"
        elif status == "pass":
            tag = "fg=black;bg=green"

        title = f"  <{tag};options=bold> {status.upper()} </> {group['title']}"
        section = group["section"]
        if group["new"]:
            self._io.write_line("")
            section.write(title)
        else:
            if self._io.output.supports_ansi():
                section.output.overwrite(title)

    def _get_decoded_crashline(self, report):
        pass

    def pytest_report_header(self, config):
        pass

    def summary_failures(self):
        # Prevent failure summary from being shown since we already
        # show the failure instantly after failure has occurred.
        pass

    def summary_errors(self):
        # Prevent error summary from being shown since we already
        # show the error instantly after error has occurred.
        pass

    def print_failure(self, report):
        pass
