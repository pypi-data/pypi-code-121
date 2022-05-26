from .sym_exception import SymException


class AccessStrategyError(SymException):
    """This is the base class for all errors that occur when initializing
    an :class:`~sym.sdk.strategies.access_strategy.AccessStrategy`.

    Args:
        name: The name of the exception (used as the second part of the error_code, e.g. STRATEGY_NOT_FOUND)
        message: The exception message to display
    """

    def __init__(self, name: str, message: str, error_type: str = "AccessStrategy"):
        super().__init__(error_type=error_type, name=name, message=message)
