import inspect

from typing import Optional


class TreatException(Exception):

    pass


class FrameAwareExceptionMixin:

    _frame: Optional[inspect.FrameInfo] = None

    def set_frame(self, frame: inspect.FrameInfo) -> None:
        self._frame = frame

    @property
    def frame(self) -> Optional[inspect.FrameInfo]:
        return self._frame
