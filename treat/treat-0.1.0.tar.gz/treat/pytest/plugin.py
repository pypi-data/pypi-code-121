import sys

from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

import pytest

from _pytest._code.code import ExceptionChainRepr
from _pytest.config import Config
from _pytest.nodes import Collector
from _pytest.outcomes import Skipped
from _pytest.reports import CollectErrorRepr
from _pytest.reports import CollectReport
from _pytest.runner import CallInfo
from cleo.formatters.formatter import Formatter
from cleo.io.inputs.string_input import StringInput
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from cleo.io.outputs.stream_output import StreamOutput
from cleo.ui.exception_trace import ExceptionTrace

from treat import test
from treat.utils.diff import Diff

from ..ui.coverage_reporter import Coverage
from .terminal_reporter import TerminalReporter
from .test_report import TestReport


if TYPE_CHECKING:
    from _pytest._code.code import ExceptionInfo
    from _pytest._code.code import ExceptionRepr
    from _pytest.python import PyCollector


def pytest_addoption(parser):
    group = parser.getgroup("cov", "coverage reporting")

    group.addoption(
        "--cov",
        action="append",
        default=[],
        metavar="SOURCE",
        nargs="?",
        const=True,
        dest="cov_source",
        help="Path or package name to measure during execution (multi-allowed). "
        "Use --cov= to not do any source filtering and record everything.",
    )


@pytest.mark.tryfirst
def pytest_load_initial_conftests(early_config, parser, args):
    options = early_config.known_args_namespace

    io = IO(StringInput(""), StreamOutput(sys.stdout), StreamOutput(sys.stderr))
    coverage = None
    if options.cov_source:
        coverage = Coverage(io, source=early_config.known_args_namespace.cov_source)
        coverage.start()

    early_config.pluginmanager.register(TreatPlugin(io, coverage), "treatplugin")


class TreatPlugin:
    def __init__(self, io: "IO", coverage: "Coverage" = None) -> None:
        self._coverage = coverage
        self._io = io

    def pytest_pycollect_makeitem(
        self, collector: "PyCollector", name: str, obj: object
    ):
        # Avoid test() from being picked up by pytest
        if obj is test:
            return []

    def pytest_runtest_makereport(self, item, call):
        return TestReport.from_item_and_call(item, call)

    def pytest_make_collect_report(self, collector: Collector) -> CollectReport:
        call = CallInfo.from_call(lambda: list(collector.collect()), "collect")
        longrepr = None
        if not call.excinfo:
            outcome = "passed"
        else:
            skip_exceptions = [Skipped]
            unittest = sys.modules.get("unittest")
            if unittest is not None:
                # Type ignored because unittest is loaded dynamically.
                skip_exceptions.append(unittest.SkipTest)  # type: ignore
            if call.excinfo.errisinstance(tuple(skip_exceptions)):
                outcome = "skipped"
                r_ = collector._repr_failure_py(call.excinfo, "line")
                assert isinstance(r_, ExceptionChainRepr), repr(r_)
                r = r_.reprcrash
                assert r
                longrepr = (str(r.path), r.lineno, r.message)
            else:
                outcome = "failed"
                errorinfo = collector.repr_failure(call.excinfo)
                if not hasattr(errorinfo, "toterminal"):
                    errorinfo = CollectErrorRepr(errorinfo)
                longrepr = errorinfo

        rep = CollectReport(
            collector.nodeid,
            outcome,
            longrepr,
            getattr(call, "result", None),
            excinfo=call.excinfo,
        )
        rep.call = call  # type: ignore # see collect_one_node

        return rep

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtestloop(self, session):
        yield

        if self._coverage:
            self._coverage.stop()

        reporter = session.config.pluginmanager.getplugin("terminalreporter")
        if reporter:
            reporter._count = len(session.items)

    @pytest.mark.trylast
    def pytest_configure(self, config):
        current_reporter = config.pluginmanager.getplugin("terminalreporter")
        config.pluginmanager.unregister(current_reporter)
        terminal_reporter = TerminalReporter(
            current_reporter.config, coverage=self._coverage
        )
        config.pluginmanager.register(terminal_reporter, "terminalreporter")

    def pytest_internalerror(
        self,
        excrepr: "ExceptionRepr",
        excinfo: "ExceptionInfo[BaseException]",
    ) -> Optional[bool]:
        io = StreamOutput(sys.stdout)
        io.set_verbosity(Verbosity.VERBOSE)
        trace = ExceptionTrace(excinfo.value)

        trace.render(io)

    # Better diffs display
    def pytest_assertrepr_compare(
        self, config: Config, op: "str", left: Any, right: Any
    ):
        if op != "==":
            return

        diff = Diff()
        output = diff.terminal_diff(left, right)

        formatter = Formatter(config.get_terminal_writer().hasmarkup)

        return [
            formatter.format(
                "<fg=red;options=bold>{}</> <fg=default;options=dark>==</> <fg=green;options=bold>{}</>".format(
                    formatter.escape(repr(left)), formatter.escape(repr(right))
                )
            ),
            "",
        ] + [formatter.format(o) for o in output]
