#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.
"""

__version__ = "0.1.0"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["Terminal"]

from sys import stdout, platform, stdin
from collections.abc import Callable
from typing import Tuple
from enum import Enum

stdout_write: Callable = stdout.write
stdout_flush: Callable = stdout.flush
char_ANSI: str = "\x1b["
char_special_ANSI: str = "\x1b"


class COLORS_MODES(Enum):
    FGCOLOR1 = "3"
    FGCOLOR2 = "9"
    BGCOLOR1 = "4"
    BGCOLOR2 = "10"


class COLORS(Enum):
    BLACK = "0m"
    RED = "1m"
    GREEN = "2m"
    YELLOW = "3m"
    BLUE = "4m"
    MAGENTA = "5m"
    CYAN = "6m"
    GRAY = "7m"
    # CUSTOM = "8m"
    DEFAULT = "9m"


colors = COLORS._member_names_
colors_map = COLORS._member_map_


class Terminal:

    """
    This class implements function to use ANSI console
    characters.
    """

    #############
    #  \x0X
    #############

    def bell() -> None:

        """
        This function play system sound.
        """

        stdout_write("\x07")
        stdout_flush()

    def backspace() -> None:

        """
        This function places the cursor on the precedent character.
        """

        stdout_write("\x08")
        stdout_flush()

    def tab() -> None:

        """
        This function places the cursor on the next multiple of 8.
        """

        stdout_write("\x09")
        stdout_flush()

    def line_feed() -> None:

        """
        This function places the cursor on the next line.
        """

        stdout_write("\x0A")
        stdout_flush()

    def carriage_return() -> None:

        """
        This function places the cursor on the first column.
        """

        stdout_write("\x0D")
        stdout_flush()

    #############
    #  \x1bX
    #############

    def save_position() -> None:

        """
        This function saves the cursor position.
        """

        stdout_write(f"{char_special_ANSI}7")
        stdout_flush()

    def restore_position() -> None:

        """
        This function restore the saved position.
        """

        stdout_write(f"{char_special_ANSI}8")
        stdout_flush()

    def clean() -> None:

        """
        This function cleans the console.
        """

        stdout_write(f"{char_special_ANSI}c")
        stdout_flush()

    #############
    #  \x1b[X
    #############

    def cursor_up(n: int = 0) -> None:

        """
        This function go to the precedent line
        (keep the same position on the precedent line).
        """

        stdout_write(f"{char_ANSI}{n}A")
        stdout_flush()

    def cursor_down(n: int = 0) -> None:

        """
        This function got to the next line
        (keep the same position on the next line).
        """

        stdout_write(f"{char_ANSI}{n}B")
        stdout_flush()

    def cursor_forward(n: int = 0) -> None:

        """
        This function go to the next character.
        """

        stdout_write(f"{char_ANSI}{n}C")
        stdout_flush()

    def cursor_back(n: int = 0) -> None:

        """
        This function go to the precedent character.
        """

        stdout_write(f"{char_ANSI}{n}D")
        stdout_flush()

    def cursor_next_line(n: int = 0) -> None:

        """
        This function go to the next line
        (on the first character of the next line).
        """

        stdout_write(f"{char_ANSI}{n}E")
        stdout_flush()

    def cursor_previous_line(n: int = 0) -> None:

        """
        This function go to the precedent line
        (on the first character of the precedent line).
        """

        stdout_write(f"{char_ANSI}{n}F")
        stdout_flush()

    def cursor_horizontal_absolute(n: int = 0) -> None:

        """
        This function go to the start of the line.
        """

        stdout_write(f"{char_ANSI}{n}G")
        stdout_flush()

    def cursor_position(line: int, position: int) -> None:

        """
        This function go to line:position.
        """

        stdout_write(f"{char_ANSI}{line};{position}H")
        stdout_flush()

    def erase_in_display(mode: int = 0) -> None:

        """
        This function clears a part of the screen.

        mode == 0 -> clear screen between cursor and end.
        mode == 1 -> clear screen between cursor and start.
        mode == 2 -> clear screen.
        mode == 3 -> clear screen and saved buffer.
        """

        if mode < 0 or mode > 3:
            raise ValueError(
                "Mode should be an integer between 0 and 3 (include)."
            )

        stdout_write(f"{char_ANSI}{mode}J")
        stdout_flush()

    def erase_in_line(n: int = 0) -> None:

        """
        This function clears a part of the line.
        """

        stdout_write(f"{char_ANSI}{n}K")
        stdout_flush()

    def scroll_up(n: int = 0) -> None:

        """
        This function scroll whole page up.
        """

        stdout_write(f"{char_ANSI}{n}S")
        stdout_flush()

    def scroll_down(n: int = 0) -> None:

        """
        This function scroll whole page down.
        """

        stdout_write(f"{char_ANSI}{n}T")
        stdout_flush()

    def cursor_horizontale_verticale_position(
        line: int, position: int
    ) -> None:

        """
        This function go to line:position.
        """

        stdout_write(f"{char_ANSI}{line};{position}f")
        stdout_flush()

    def device_status_report() -> Tuple[bytes, bytes]:

        """
        This function reports the cursor position.
        """

        stdout_write(f"{char_ANSI}6n")
        stdout_flush()

        reader = stdin.buffer.read
        stdin.reconfigure(newline="")
        stdin.flush()
        data = reader(1)
        precedent = b""
        position = b""

        while data != b"\x1b":
            precedent += data
            data = reader(1)

        while data != b"R":
            position += data
            data = reader(1)

        position += data

        return precedent, position

    def save_current_cursor_position() -> None:

        """
        This function save the cursor position.
        """

        stdout_write(f"{char_ANSI}s")
        stdout_flush()

    def restore_saved_cursor_position() -> None:

        """
        This function save the cursor position.
        """

        stdout_write(f"{char_ANSI}u")
        stdout_flush()

    #############
    #  \x1b[Xm  (GRAPHIC)
    #############

    def reset() -> None:

        """
        This function resets colors (background and foreground).
        """

        stdout_write(f"{char_ANSI}0m")
        stdout_flush()

    def bold() -> None:

        """
        This function adds bold.
        """

        stdout_write(f"{char_ANSI}1m")
        stdout_flush()

    def faint() -> None:

        """
        This function adds intensity.
        """

        stdout_write(f"{char_ANSI}2m")
        stdout_flush()

    def italic() -> None:

        """
        This function adds italic.
        """

        stdout_write(f"{char_ANSI}3m")
        stdout_flush()

    def underline() -> None:

        """
        This function adds underline.
        """

        stdout_write(f"{char_ANSI}4m")
        stdout_flush()

    def slow_blink() -> None:

        """
        Sets blinking to less than 150 times per minute.
        """

        stdout_write(f"{char_ANSI}5m")
        stdout_flush()

    def rapid_blink() -> None:

        """
        Sets blinking to greter than 150 times per minute.
        """

        stdout_write(f"{char_ANSI}6m")
        stdout_flush()

    def reverse() -> None:

        """
        This function reverses colors (background/foreground).
        """

        stdout_write(f"{char_ANSI}7m")
        stdout_flush()

    def hide() -> None:

        """
        This function adds hide.
        """

        stdout_write(f"{char_ANSI}8m")
        stdout_flush()

    def strike() -> None:

        """
        Characters legible but marked as if for deletion.
        """

        stdout_write(f"{char_ANSI}9m")
        stdout_flush()

    def font(font: int) -> None:

        """
        This function changes font.
        """

        if font > 9:
            raise ValueError(f"font ({font}) should be smaller than 10")

        font += 10
        stdout_write(f"{char_ANSI}{font}m")
        stdout_flush()

    def gothic() -> None:

        """
        Characters legible but marked as if for deletion.
        """

        stdout_write(f"{char_ANSI}20m")
        stdout_flush()

    def no_bold() -> None:

        """
        This function removes bold.
        """

        stdout_write(f"{char_ANSI}21m")
        stdout_flush()

    def no_intensity() -> None:

        """
        This function removes intensity.
        """

        stdout_write(f"{char_ANSI}22m")
        stdout_flush()

    def no_italic() -> None:

        """
        This function removes italic.
        """

        stdout_write(f"{char_ANSI}23m")
        stdout_flush()

    def no_underline() -> None:

        """
        This function removes underline.
        """

        stdout_write(f"{char_ANSI}24m")
        stdout_flush()

    def no_blink() -> None:

        """
        This function removes underline.
        """

        stdout_write(f"{char_ANSI}25m")
        stdout_flush()

    def no_reverse() -> None:

        """
        This function replace colors (background/foreground).
        """

        stdout_write(f"{char_ANSI}27m")
        stdout_flush()

    def no_hide() -> None:

        """
        This function removes hide.
        """

        stdout_write(f"{char_ANSI}28m")
        stdout_flush()

    def not_crossed_out() -> None:

        """
        This function removes hide.
        """

        stdout_write(f"{char_ANSI}29m")
        stdout_flush()

    def change_foreground_color_3bytes(
        red: int, green: int, blue: int
    ) -> None:

        """
        This function changes foreground color
        using the 3 bytes mode.
        """

        if red > 255 or green > 255 or blue > 255:
            raise ValueError(
                f"colors ({red};{green};{blue}) should be in range of 0 to 255"
            )

        stdout_write(f"{char_ANSI}38;2;{red};{green};{blue}m")
        stdout_flush()

    def change_foreground_color_8bits(color: int) -> None:

        """
        This function changes foreground color
        using the 8 bits mode.

        2**3 == 8 -> RED
        2**3 == 8 -> GREEN
        2**2 == 4 -> BLUE

        RRRGGGBB

        (0b111 << 5) + (0b111 << 2) + 0b11

        (7 << 5) + (7 << 2) + 3
        """

        if color > 255 or color < 0:
            raise ValueError(f"color ({color}) should be in range of 0 to 255")

        stdout_write(f"{char_ANSI}38;5;{color}")
        stdout_flush()

    def change_background_color_3bytes(
        red: int, green: int, blue: int
    ) -> None:

        """
        This function changes background color
        using the 3 bytes mode.
        """

        if (
            red > 255
            or red < 0
            or green > 255
            or green < 0
            or blue > 255
            or blue < 0
        ):
            raise ValueError(
                f"colors ({red};{green};{blue}) should be in range of 0 to 255"
            )

        stdout_write(f"{char_ANSI}48;2;{red};{green};{blue}m")
        stdout_flush()

    def change_background_color_8bits(color: int) -> None:

        """
        This function changes background color
        using the 8 bits mode.
        """

        if color > 255 or color < 0:
            raise ValueError(f"color ({color}) should be in range of 0 to 255")

        stdout_write(f"{char_ANSI}48;5;{color}")
        stdout_flush()

    def change_foreground_color(color: str, mode: int = 1) -> None:

        """
        This function changes foreground color.
        """

        color = color.upper()

        if mode == 1:
            mode = COLORS_MODES.FGCOLOR1.value
        elif mode == 2:
            mode = COLORS_MODES.FGCOLOR2.value
        else:
            raise ValueError(f"mode ({mode}) sould be 1 or 2")

        if color not in colors:
            raise ValueError(f"color ({color}) should be in {colors}")

        color = colors_map[color].value

        stdout_write(f"{char_ANSI}{mode}{color}")
        stdout_flush()

    def change_background_color(color: str, mode: int = 1) -> None:

        """
        This function changes background color.
        """

        color = color.upper()

        if mode == 1:
            mode = COLORS_MODES.BGCOLOR1.value
        elif mode == 2:
            mode = COLORS_MODES.BGCOLOR2.value
        else:
            raise ValueError(f"mode ({mode}) sould be 1 or 2")

        if color not in colors:
            raise ValueError(f"color ({color}) should be in {colors}")

        color = colors_map[color].value

        stdout_write(f"{char_ANSI}{mode}{color}")
        stdout_flush()

    def reset_background() -> None:

        """
        This function resets the background color.
        """

        stdout_write(f"{char_ANSI}39m")
        stdout_flush()

    def reset_foreground() -> None:

        """
        This function resets the foreground color.
        """

        stdout_write(f"{char_ANSI}49m")
        stdout_flush()


if platform == "win32":

    class Terminal(Terminal):

        __doc__ = Terminal.__doc__
