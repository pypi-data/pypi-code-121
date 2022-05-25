import sys
import traceback
from typing import Callable, List, Optional

from .models import Call, Error


class WrappedFunction:
    def __init__(
        self,
        function: Callable,
        labels: Optional[List[str]] = None,
    ):
        self._labels = labels if labels is not None else []
        self._name = _get_qualified_name(function)
        self._calls: List[Call] = []

        self._function = function

    def __call__(self, *args, **kwargs):
        error = None
        try:
            output = self._function(*args, **kwargs)
            self.calls.append(Call())
            return output
        except Exception as exception:
            error_type, _, error_tb = sys.exc_info()

            # The current frame is for `WrappedFunction.__call__`. Because
            # `WrappedFunction.__call__` is irrelevant to the user, we skip
            # to the next frame.
            error_tb = error_tb.tb_next

            filename = error_tb.tb_frame.f_code.co_filename
            line_number = error_tb.tb_lineno
            traceback_msg = "".join(
                traceback.format_exception(error_type, _, error_tb, chain=True)
            )

            error = Error(
                traceback=traceback_msg,
                line=line_number,
                module=filename,
                type=error_type.__name__,
            )
            self.calls.append(Call(error=error))
            raise exception

    @property
    def labels(self) -> List[str]:
        return self._labels

    @property
    def name(self) -> str:
        return self._name

    @property
    def calls(self) -> List[Call]:
        return self._calls


def _get_qualified_name(func):
    return f"{func.__module__}.{func.__name__}"
