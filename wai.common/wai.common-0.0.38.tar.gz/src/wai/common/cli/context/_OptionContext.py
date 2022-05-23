from ..options import Option


class OptionContext:
    """
    Base class for option contexts.
    """
    def __init__(self, option: Option, context):
        self._option: Option = option
        self._context = context
