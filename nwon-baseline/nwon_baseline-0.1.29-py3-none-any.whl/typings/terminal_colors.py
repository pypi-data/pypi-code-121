from enum import Enum


class TerminalColors(Enum):
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"


class TerminalStyling(Enum):
    HEADER = "\033[95m"
    END_CHARACTER = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


__all__ = ["TerminalColors", "TerminalStyling"]
