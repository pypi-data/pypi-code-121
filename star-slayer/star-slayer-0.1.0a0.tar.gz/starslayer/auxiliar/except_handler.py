"""
This handler ensures that any exception is also caught by the logger.
"""

import sys
from types import TracebackType
from typing import Any

from ..logger import GameLogger


# pylint: disable=invalid-name
def except_handler(_type: type[BaseException],
                   value: BaseException,
                   _tb: TracebackType | None) -> Any:
    """
    Handles an exception and passes onto the logger.
    """

    GameLogger().exception(f"Unexpected Exception Ocurred:\n\n{value}")

sys.excepthook = except_handler
