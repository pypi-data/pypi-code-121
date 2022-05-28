import inspect

from typing import Optional

from treat.exceptions import FrameAwareExceptionMixin
from treat.exceptions import TreatException
from treat.ui.errors import UIError


class MockError(TreatException, UIError):

    pass


class FrameAwareMockError(MockError, FrameAwareExceptionMixin):
    def __init__(
        self, *args, frame: Optional[inspect.FrameInfo] = None, **kwargs
    ) -> None:
        self.set_frame(frame)

        super().__init__(*args, **kwargs)


class InvalidMockCallsCount(FrameAwareMockError):

    MESSAGE_FORMAT = (
        "Expected <fg=cyan>{name}</>() to {expected_message} "
        "but it was actually {got_message}."
    )

    def __init__(
        self,
        name: str,
        expected: int,
        got: int,
        frame: Optional[inspect.FrameInfo] = None,
    ) -> None:
        self._name = name
        self._expected = expected
        self._got = got
        self._message = self.MESSAGE_FORMAT.format(
            name=self._name,
            expected_message=self._get_call_message(expected),
            got_message=self._get_call_message(got, expected=False),
        )

        super().__init__(self.remove_format(self._message), frame=frame)

    @property
    def pretty_error(self) -> str:
        return self._message

    def _get_call_message(self, value: int, expected: bool = True) -> str:
        color = "green"
        if not expected:
            color = "red"

        never = ""
        if value == 0:
            never = "never "

        if expected:
            message = never + "be called"
        else:
            message = never + "called"

        if value == 1:
            message += f" <fg={color};options=bold>once</>"
        elif value == 2:
            message += f" <fg={color};options=bold>twice</>"
        else:
            message += f" <fg={color};options=bold>{value}</> times"

        return message
