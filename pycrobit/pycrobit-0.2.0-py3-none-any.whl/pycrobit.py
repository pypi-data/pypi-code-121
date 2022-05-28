"""
Recycle microbits exercises in python using 5 * 5 strings and some coloring.
"""

__all__ = ["Pycrobit", "DEFAULT_COLOR_MAP"]

import os
import time
from typing import Dict

try:
    from colorama import Fore, init

    init()
except ImportError:

    class Fore:  # pylint: disable=too-few-public-methods
        """Good enough replacement for colorama."""

        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        RESET = "\033[0m"


DEFAULT_COLOR_MAP = {".": "", "*": Fore.RED}
ColorMap = Dict[str, str]


def validate_pycrobit_str(pycrobit_string: str) -> str:
    """Validate that the pycrobit string is correct."""
    strip_line_feed = pycrobit_string.strip("\n ")
    if len(strip_line_feed) == 25:
        result = ""
        for i, char in enumerate(strip_line_feed):
            result += char
            if i % 5 == 4:
                result += "\n"
        return result
    lines = strip_line_feed.split("\n")
    assert len(lines) == 5, f"We expected 5 lines in the string and got {lines} "
    for i, line in enumerate(lines):
        stripped_line = line.strip(" ")
        if len(stripped_line) != 5:
            raise ValueError(
                f"We expected 5 characters on line n°{i+1} and got "
                f"{len(stripped_line)} ({stripped_line})"
            )
    return pycrobit_string


def validate_color_map(color_map: ColorMap) -> None:
    """Validate that the color map is correct."""
    for character, color in color_map.items():
        if not isinstance(color, str):
            msg = f"The color '{color}' for '{character}' is invalid."
            raise ValueError(msg)


def clear_terminal() -> None:
    """Clear the terminal (refresh the screen)."""
    os.system("cls" if os.name == "nt" else "clear")


def colorize(pycrobit_string: str, color_map: ColorMap) -> str:
    """Colorize a string to be displayed in terminal."""
    validated_str = validate_pycrobit_str(pycrobit_string)
    validate_color_map(color_map)
    return "".join(f"{color_map.get(px, '')}{px}{Fore.RESET}" for px in validated_str)


class Pycrobit:

    """A context manager that act similarly as a microbit but in Python."""

    DEFAULT_FRAMERATE_SECOND = 1.0

    def __init__(self, framerate=DEFAULT_FRAMERATE_SECOND):
        # No delay for the first display
        self.framerate = framerate
        self._switch_frame_after = 0

    def wait(self, time_to_wait: float = 0.0):
        """Wait for an additional 'time_to_wait'.

        It can be negative to accelerate the framerate."""
        if self._switch_frame_after + time_to_wait < 0:
            raise ValueError("pycrobit was asked to wait for a negative time.")
        self._switch_frame_after += time_to_wait

    def display(self, pycrobit_string: str, color_map: ColorMap = None):
        """Display the string"""
        # print(f"entering {pycrobit_string}")
        clear_terminal()
        if color_map is None:
            color_map = DEFAULT_COLOR_MAP
        print(colorize(pycrobit_string, color_map))
        time.sleep(self._switch_frame_after)
        self._switch_frame_after = self.framerate
