import inspect

from typing import Optional
from typing import Union

from cleo.io.io import IO
from cleo.io.outputs.output import Output
from cleo.ui.exception_trace import ExceptionTrace as _ExceptionTrace
from cleo.ui.exception_trace import Highlighter
from crashtest.frame import Frame
from crashtest.solution_providers.solution_provider_repository import (
    SolutionProviderRepository,
)

from treat.mock.exceptions import FrameAwareMockError

from .errors import UIError


class ExceptionTrace(_ExceptionTrace):
    def __init__(
        self,
        exception: Exception,
        solution_provider_repository: Optional[SolutionProviderRepository] = None,
        base_indent: int = 0,
    ) -> None:
        super().__init__(
            exception, solution_provider_repository=solution_provider_repository
        )

        self._base_indent = base_indent

    def _render_exception(self, io, exception):
        from crashtest.inspector import Inspector

        inspector = Inspector(exception)
        if not inspector.frames:
            return

        frames = inspector.frames
        # For mock errors we actually want to reference
        # the initial expection line instead of the internal
        # line where the expection is raised.
        # In order to do so, we get the initial frame of the expection
        # and add it to the stack trace.
        if (
            isinstance(self._exception, FrameAwareMockError)
            and self._exception.frame is not None
        ):
            frame = Frame(self._exception.frame)
            frames.append(frame)

        self._render_trace(io, frames)

        self._render_line(
            io, "<error>{}</error>".format(inspector.exception_name), True
        )
        io.write_line("")
        if isinstance(exception, UIError):
            exception_message = exception.pretty_error.replace("\n", "\n  ")
        elif isinstance(exception, AssertionError):
            exception_message = inspector.exception_message.replace("\n", "\n  ")
        else:
            exception_message = io.remove_format(inspector.exception_message).replace(
                "\n", "\n  "
            )

        self._render_line(io, "<b>{}</b>".format(exception_message))

        current_frame = inspector.frames[-1]
        self._render_snippet(
            io, current_frame, complete=isinstance(exception, AssertionError)
        )

        self._render_solution(io, inspector)

    def _render_snippet(
        self, io: Union[IO, Output], frame: Frame, complete: bool = False
    ):
        self._render_line(
            io,
            "at <fg=green>{}</>:<b>{}</b> in <fg=cyan>{}</>".format(
                self._get_relative_file_path(frame.filename),
                frame.lineno,
                frame.function,
            ),
            True,
        )

        if complete:
            start_line = frame.frame.f_code.co_firstlineno
            lines_before = frame.lineno - start_line + 1
            lines = inspect.getsourcelines(frame.frame.f_code)[0]
            lines_after = start_line + len(lines) - frame.lineno
        else:
            lines_before = lines_after = 4

        code_lines = Highlighter(supports_utf8=io.supports_utf8()).code_snippet(
            frame.file_content,
            frame.lineno,
            lines_before,
            lines_after,
        )

        for code_line in code_lines:
            self._render_line(io, code_line, indent=4)

    def _render_line(
        self, io: Output, line: str, new_line: bool = False, indent: int = 2
    ) -> None:
        indent += self._base_indent

        return super()._render_line(io, line, new_line=new_line, indent=indent)
