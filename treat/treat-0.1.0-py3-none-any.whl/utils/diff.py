import re

from difflib import ndiff
from typing import Any
from typing import List
from unittest import mock

import pprintpp

from cleo.formatters.formatter import Formatter


# Register extra types so that they have a nice
# diff on assertion errors.
types_to_register = [
    (mock._CallList, ("list", "[", "]", "[]")),
]

pprintpp.PrettyPrinter._open_close_empty.update(
    pprintpp._mk_open_close_empty_dict(types_to_register)
)


class DiffError(Exception):

    pass


class IncompatibleTypes(DiffError):
    def __init__(self, type1, type2) -> None:
        super().__init__(f"Incompatible types for diff: {type1} and {type2}")


class Diff:
    def __init__(self, width: int = 80) -> None:
        self._width = width

    def terminal_diff(self, left: Any, right: Any) -> List[str]:
        formatter = Formatter()
        pretty_left = [
            formatter.escape(line) for line in self.prettify(left).splitlines()
        ]
        pretty_right = [
            formatter.escape(line) for line in self.prettify(right).splitlines()
        ]

        output = []
        for diff in ndiff(pretty_left, pretty_right):
            if diff.startswith("? "):
                line = output.pop(-1)
                line = formatter.remove_format(line)
                fg = "black" if line.startswith("- ") else "black"
                bg = "red" if line.startswith("- ") else "green"
                for m in reversed(list(re.finditer(r"[\^\-+]+", diff))):
                    line = (
                        line[: m.start()]
                        + f"<fg={fg};bg={bg};options=bold>{line[m.start():m.end()]}</>"
                        + line[m.end() :]
                    )

                diff = line

            if diff.startswith("- "):
                output.append(f"<fg=red;options=bold>{diff}</>")
            elif diff.startswith("+ "):
                output.append(f"<fg=green;options=bold>{diff}</>")
            else:
                output.append(f"<fg=default>{diff}</>")

        return output

    def prettify(self, element: Any) -> str:
        if isinstance(element, str):
            return element

        return pprintpp.pformat(element, width=self._width)
