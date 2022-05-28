import re

from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from _pytest.reports import TestReport


class TestResult:

    FAIL = "failed"
    SKIPPED = "skipped"
    RUNS = "pending"
    PASS = "passed"

    def __init__(
        self,
        identifier: str,
        description: str,
        type: str,
        icon: str,
        color: str,
        action: str,
        error: Exception = None,
        stdout: str = None,
        skip_reason: Optional[str] = None,
        parameters: Optional[List[Tuple[str, Any]]] = None,
    ) -> None:
        self._identifier = identifier
        self._description = description
        self._type = type
        self._icon = icon
        self._color = color
        self._action = action
        self._error = error
        self._stdout = stdout
        self._skip_reason = skip_reason

        if parameters is None:
            parameters = []

        self._parameters: List[Tuple[str, Any]] = parameters

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def base_identifier(self) -> str:
        return re.sub(r"\[(.+)\]$", "", self._identifier)

    @property
    def group(self) -> str:
        return self._group

    @property
    def description(self) -> str:
        return self._description

    @property
    def type(self) -> str:
        return self._type

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def color(self) -> str:
        return self._color

    @property
    def action(self) -> str:
        return self._action

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    @property
    def stdout(self) -> Optional[str]:
        return self._stdout

    @property
    def skip_reason(self) -> Optional[str]:
        return self._skip_reason

    def is_skipped(self) -> bool:
        return self._type == self.SKIPPED

    @property
    def parameters(self) -> List[Tuple[str, Any]]:
        return self._parameters

    @classmethod
    def create_from_test_report(
        cls, report: TestReport, type: Optional[str] = None
    ) -> "TestResult":
        identifier = report.nodeid
        description = cls.make_description(report)
        icon = cls.make_icon(report)
        color = cls.make_color(report)
        type = type or cls.make_type(report)
        action = report.when
        stdout = None
        if hasattr(report, "sections"):
            for name, content in report.sections:
                if "stdout" in name:
                    stdout = content

        return TestResult(
            identifier,
            description,
            type,
            icon,
            color,
            action,
            error=report.exception if type == cls.FAIL else None,
            stdout=stdout,
            skip_reason=report.longrepr[2][9:]
            if report.outcome == cls.SKIPPED
            else None,
            parameters=list(report.parameters.items()),
        )

    @classmethod
    def make_description(cls, record: TestReport) -> str:
        description = record.description
        if not description:
            description = record.nodeid.split("::")[-1]

            # Replace underscores with spaces
            description = description.replace("_", " ")

            # If it starts with `test_`, we remove it
            description = re.sub("^test(.*)", "\\1", description)

            # Remove spaces
            description = description.strip()

            # Drop parameters since they will be handle by the Style instance
            description = re.sub(r"\[(.+)\]$", "", description)

        return description

    @classmethod
    def make_icon(cls, record: TestReport) -> str:
        if record.outcome == cls.FAIL:
            return "✕"
        elif record.outcome == cls.SKIPPED:
            return "s"
        elif record.when in ["setup", "call"]:
            return "•"

        return "✓"

    @classmethod
    def make_color(cls, record: TestReport) -> str:
        if record.outcome == cls.FAIL:
            return "red"
        elif record.outcome == cls.SKIPPED:
            return "yellow"
        elif record.when in ["setup", "call"]:
            return "blue"

        return "green"

    @classmethod
    def make_type(cls, record: TestReport) -> str:
        if record.outcome == cls.FAIL:
            return cls.FAIL
        elif record.outcome == cls.SKIPPED:
            return cls.SKIPPED
        elif record.when in ["setup", "call"]:
            return cls.RUNS

        return cls.PASS
