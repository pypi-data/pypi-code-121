from typing import Optional
from typing import Tuple

from _pytest._code.code import ExceptionInfo
from _pytest.nodes import Item
from _pytest.outcomes import skip
from _pytest.reports import TestReport as BaseTestReport


class TestReport(BaseTestReport):
    def __init__(
        self,
        nodeid,
        location: Tuple[str, Optional[int], str],
        keywords,
        outcome,
        longrepr,
        when,
        sections=(),
        duration=0,
        user_properties=None,
        description=None,
        **extra
    ) -> None:
        super().__init__(
            nodeid,
            location,
            keywords,
            outcome,
            longrepr,
            when,
            sections=sections,
            duration=duration,
            user_properties=user_properties,
            description=description,
            **extra
        )

    @classmethod
    def from_item_and_call(cls, item: Item, call) -> "TestReport":
        callspec = item.callspec if hasattr(item, "callspec") else None
        parameters = callspec.params if callspec else {}
        when = call.when
        duration = call.stop - call.start
        keywords = {x: 1 for x in item.keywords}
        excinfo = call.excinfo
        sections = []
        exception = call.excinfo
        if not call.excinfo:
            outcome = "passed"
            longrepr = None
        else:
            if not isinstance(excinfo, ExceptionInfo):
                outcome = "failed"
                longrepr = excinfo
            elif excinfo.errisinstance(skip.Exception):
                outcome = "skipped"
                r = excinfo._getreprcrash()
                longrepr = (str(r.path), r.lineno, r.message)
            else:
                outcome = "failed"
                if call.when == "call":
                    longrepr = item.repr_failure(excinfo)
                else:  # exception in setup or teardown
                    longrepr = item._repr_failure_py(
                        excinfo, style=item.config.getoption("tbstyle", "auto")
                    )
        for rwhen, key, content in item._report_sections:
            sections.append(("Captured {} {}".format(key, rwhen), content))

        description = item.obj.__doc__
        if description is not None:
            description_parts = description.strip().split("\n", 1)
            description = description_parts[0]
            description = description.strip()

        return cls(
            item.nodeid,
            item.location,
            keywords,
            outcome,
            longrepr,
            when,
            sections,
            duration,
            user_properties=item.user_properties,
            exception=exception,
            parameters=parameters,
            description=description,
        )
