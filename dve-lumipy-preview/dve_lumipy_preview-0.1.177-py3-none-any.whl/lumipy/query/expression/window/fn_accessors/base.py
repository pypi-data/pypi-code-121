from ..function import WindowAggregate
from ..over import Over


class BaseWindowFunctionAccessor:

    def __init__(self, window: Over):
        self._window = window

    def _apply(self, expression):
        return WindowAggregate(self._window, expression)
