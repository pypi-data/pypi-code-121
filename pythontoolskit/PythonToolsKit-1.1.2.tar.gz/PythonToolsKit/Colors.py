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

For all these features, you have the basic method, the "check" method
and the "safe" method. The "check" method verifies the validity of the
arguments and raises a ValueError when the arguments are invalid. The
"safe" can construct valid parameters from invalid parameters.

>>> from Colors import *
>>> Colors.int_to_html(255, 0, 150)
'#ff0096'
>>> Colors.html_to_int('#ff0096')
(255, 0, 150)
>>> Colors.html_to_int('#FF0096')
(255, 0, 150)
>>> Colors.rgb_to_int('rgb(255, 0, 150)')
(255, 0, 150)
>>> Colors.rgba_to_int('rgba(255, 0, 150, 0.5)')
(255, 0, 150)
>>> Colors.int_to_rgba(255, 0, 150)
'rgba(255, 0, 150, 1)'
>>> Colors.int_to_rgb(255, 0, 150)
'rgb(255, 0, 150)'
>>> Colors.get_8bits_color(7, 7, 3)
255
>>> Colors.get_8bits_color(0, 0, 0)
0
>>>

Run tests:
 ~# python -m doctest Colors.py
 ~# python Colors.py            # Verbose mode

22 items passed all tests:
  10 tests in __main__
   4 tests in __main__.Colors.check_get_8bits_color
   5 tests in __main__.Colors.check_html_to_int
   4 tests in __main__.Colors.check_int_to_html
   4 tests in __main__.Colors.check_int_to_rgb
   4 tests in __main__.Colors.check_int_to_rgba
  10 tests in __main__.Colors.check_rgb_to_int
  12 tests in __main__.Colors.check_rgba_to_int
   2 tests in __main__.Colors.get_8bits_color
   2 tests in __main__.Colors.html_to_int
   1 tests in __main__.Colors.int_to_html
   1 tests in __main__.Colors.int_to_rgb
   1 tests in __main__.Colors.int_to_rgba
   1 tests in __main__.Colors.rgb_to_int
   1 tests in __main__.Colors.rgba_to_int
   2 tests in __main__.Colors.safe_get_8bits_color
   2 tests in __main__.Colors.safe_html_to_int
   2 tests in __main__.Colors.safe_int_to_html
   2 tests in __main__.Colors.safe_int_to_rgb
   2 tests in __main__.Colors.safe_int_to_rgba
   3 tests in __main__.Colors.safe_rgb_to_int
   3 tests in __main__.Colors.safe_rgba_to_int
78 tests in 23 items.
78 passed and 0 failed.
Test passed.

~# coverage run Colors.py
~# coverage report
Name        Stmts   Miss  Cover
-------------------------------
Colors.py     176      0   100%
-------------------------------
TOTAL         176      0   100%
~#
"""

__version__ = "0.0.1"
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

__all__ = ["Colors"]

from binascii import b2a_hex, a2b_hex
from decimal import Decimal
from typing import Tuple


class Colors:

    """
    This class implements functions to translate colors.
    """

    def check_int_to_html(*args) -> str:

        """
        This function performs checks for int_to_html
        arguments and call it.

        >>> Colors.check_int_to_html(255, 0, 150)
        '#ff0096'
        >>> Colors.check_int_to_html(256, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_html arguments should be int between 0 and 255 (256 is invalid).
        >>> Colors.check_int_to_html(255, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_html arguments should be int between 0 and 255 (-1 is invalid).
        >>> Colors.check_int_to_html(255, 0, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_html arguments should be int between 0 and 255 ('invalid' is invalid).
        >>>
        """

        for arg in args:
            if not isinstance(arg, int) or arg > 255 or arg < 0:
                raise ValueError(
                    "Colors.int_to_html arguments should "
                    f"be int between 0 and 255 ({arg!r} is invalid)."
                )

        return Colors.int_to_html(*args)

    def safe_int_to_html(*args) -> str:

        """
        This function performs checks for int_to_html
        arguments and call it.

        >>> Colors.safe_int_to_html(255, 0, 150)
        '#ff0096'
        >>> Colors.safe_int_to_html(256, -1, "invalid")
        '#00ff00'
        >>>
        """

        args_ = []
        append = args_.append
        for i, arg in enumerate(args):
            if not isinstance(arg, int):
                arg = 0
            else:
                arg = arg % 256

            append(arg)

        return Colors.int_to_html(*args_)

    def int_to_html(red: int, green: int, blue: int) -> str:

        """
        This function translates integers colors to HTML colors.

        >>> Colors.int_to_html(255, 0, 150)
        '#ff0096'
        >>>
        """

        return "#" + b2a_hex(bytes((red, green, blue))).decode()

    def check_html_to_int(color: str) -> Tuple[int, int, int]:

        """
        This function performs checks for html_to_int
        arguments and call it.

        >>> Colors.check_html_to_int('#FF0096')
        (255, 0, 150)
        >>> Colors.check_html_to_int(7)
        Traceback (most recent call last):
                ...
        ValueError: Color should be a hexadecimal string of length 7 starting with '#' (7 is invalid).
        >>> Colors.check_html_to_int('')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a hexadecimal string of length 7 starting with '#' ('' is invalid).
        >>> Colors.check_html_to_int('!FF0096')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a hexadecimal string of length 7 starting with '#' ('!FF0096' is invalid).
        >>> Colors.check_html_to_int('#ZF0096')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a hexadecimal string of length 7 starting with '#' ('#ZF0096' is invalid).
        >>>
        """

        if (
            not isinstance(color, str)
            or len(color) != 7
            or color[0] != "#"
            or any(x not in "abcdefABCDEF0123456789" for x in color[1:])
        ):
            raise ValueError(
                "Color should be a hexadecimal "
                "string of length 7 starting with"
                f" '#' ({color!r} is invalid)."
            )

        return Colors.html_to_int(color)

    def safe_html_to_int(color: str) -> Tuple[int, int, int]:

        """
        This function performs checks for html_to_int
        arguments and call it.

        >>> Colors.safe_html_to_int('#FF0096')
        (255, 0, 150)
        >>> Colors.safe_html_to_int('!FF0Z')
        (255, 0, 0)
        >>>
        """

        color_ = "#"
        for char in color:
            if char in "abcdefABCDEF0123456789":
                color_ += char

            if len(color_) >= 7:
                break

        while len(color_) < 7:
            color_ += "0"

        return Colors.html_to_int(color_)

    def html_to_int(colors: str) -> Tuple[int, int, int]:

        """
        This function translates HTML colors to integers colors.

        >>> Colors.html_to_int('#FF0096')
        (255, 0, 150)
        >>> Colors.html_to_int('#ff0096')
        (255, 0, 150)
        >>>
        """

        return tuple(x for x in a2b_hex(colors[1:].encode()))

    def check_rgb_to_int(color: str) -> Tuple[int, int, int]:

        """
        This function performs checks for rgb_to_int
        arguments and call it.

        >>> Colors.check_rgb_to_int('rgb(255, 0, 150)')
        (255, 0, 150)
        >>> Colors.check_rgb_to_int('rgb ( 255 , 0 , 150 ) ')
        (255, 0, 150)
        >>> Colors.check_rgb_to_int(7)
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') (7 is invalid).
        >>> Colors.check_rgb_to_int('')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('' is invalid).
        >>> Colors.check_rgb_to_int('rgb')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('rgb' is invalid).
        >>> Colors.check_rgb_to_int('rgb(')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('rgb(' is invalid).
        >>> Colors.check_rgb_to_int('rgb()')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('rgb()' is invalid).
        >>> Colors.check_rgb_to_int('rgb(,,)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('rgb(,,)' is invalid).
        >>> Colors.check_rgb_to_int('rgb(256, -1, 5)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('rgb(256, -1, 5)' is invalid).
        >>> Colors.check_rgb_to_int('rgb(255, -1, 5)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbg' call with three byte values separated by commas (example: 'rgb(255, 0, 2)') ('rgb(255, -1, 5)' is invalid).
        >>>
        """

        invalid = (
            not isinstance(color, str)
            or not color.startswith("rgb")
            or "(" not in color
            or ")" not in color
        )
        if not invalid:
            colors = color.lstrip("rgb( ").rstrip(") ").split(",")
            invalid = (
                len(colors) != 3
                or any(not x.strip().isdigit() for x in colors)
                or any(0 > int(x) > 255 for x in colors)
            )

        if invalid:
            raise ValueError(
                "Color should be a string of 'rbg' call with "
                "three byte values separated by commas (example:"
                f" 'rgb(255, 0, 2)') ({color!r} is invalid)."
            )

        return Colors.rgb_to_int(color)

    def safe_rgb_to_int(color: str) -> Tuple[int, int, int]:

        """
        This function performs checks for rgb_to_int
        arguments and call it.

        >>> Colors.safe_rgb_to_int('rgb(255, 0, 150)')
        (255, 0, 150)
        >>> Colors.safe_rgb_to_int('rgb(255, 0, 150,)')
        (255, 0, 150)
        >>> Colors.safe_rgb_to_int('azerty | qwe255, rty1500 |')
        (255, 220, 0)
        >>>
        """

        color_ = "rgb("
        counter = 0
        temp_color = ""
        for char in color:
            if char in "0123456789":
                temp_color += char

            if char == ",":
                counter += 1
                color_ += str(int(temp_color) % 256) + ", "
                temp_color = ""

                if counter == 3:
                    break

        if temp_color:
            counter += 1
            color_ += str(int(temp_color) % 256) + ", "

        while counter < 3:
            color_ += "0, "
            counter += 1

        return Colors.rgb_to_int(color_[:-2] + ")")

    def rgb_to_int(colors: str) -> Tuple[int, int, int]:

        """
        This function translates RGB (CSS function)
        colors to integers colors.

        >>> Colors.rgb_to_int('rgb(255, 0, 150)')
        (255, 0, 150)
        >>>
        """

        return tuple(int(x) for x in colors.strip("rgb() ").split(","))

    def check_rgba_to_int(color: str) -> Tuple[int, int, int]:

        """
        This function performs checks for rgba_to_int
        arguments and call it.

        >>> Colors.check_rgba_to_int('rgba(255, 0, 150, 0.0)')
        (255, 0, 150)
        >>> Colors.rgba_to_int('rgba ( 255 , 0 , 150 , 1) ')
        (255, 0, 150)
        >>> Colors.check_rgba_to_int(7)
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') (7 is invalid).
        >>> Colors.check_rgba_to_int('')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('' is invalid).
        >>> Colors.check_rgba_to_int('rgba')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba' is invalid).
        >>> Colors.check_rgba_to_int('rgba(')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba(' is invalid).
        >>> Colors.check_rgba_to_int('rgba()')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba()' is invalid).
        >>> Colors.check_rgba_to_int('rgba(,,)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba(,,)' is invalid).
        >>> Colors.check_rgba_to_int('rgba(256, -1, 5, 0.5)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba(256, -1, 5, 0.5)' is invalid).
        >>> Colors.check_rgba_to_int('rgba(255, -1, 5, 0.5)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba(255, -1, 5, 0.5)' is invalid).
        >>> Colors.check_rgba_to_int('rgba(255, 0, 5, 0.5.5)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba(255, 0, 5, 0.5.5)' is invalid).
        >>> Colors.check_rgba_to_int('rgba(255, 0, 5, 1.5)')
        Traceback (most recent call last):
                ...
        ValueError: Color should be a string of 'rbga' call with three byte values separated by commas and a float between 0 and 1 (example: 'rgba(255, 0, 2, 0.5)') ('rgba(255, 0, 5, 1.5)' is invalid).
        >>>
        """

        invalid = (
            not isinstance(color, str)
            or not color.startswith("rgba")
            or "(" not in color
            or ")" not in color
        )
        if not invalid:
            colors = color.lstrip("rgba( ").rstrip(") ").split(",")
            invalid = (
                len(colors) != 4
                or any(not x.strip().isdigit() for x in colors[:-1])
                or any(0 > int(x) > 255 for x in colors[:-1])
                or not "".join(colors[-1].split(".", 1)).strip().isdigit()
            )
            if not invalid:
                transparency = float(colors[-1])
                invalid = 0 > transparency or transparency > 1

        if invalid:
            raise ValueError(
                "Color should be a string of 'rbga' call with "
                "three byte values separated by commas and a float between 0 and 1"
                f" (example: 'rgba(255, 0, 2, 0.5)') ({color!r} is invalid)."
            )

        return Colors.rgba_to_int(color)

    def safe_rgba_to_int(color: str) -> Tuple[int, int, int]:

        """
        This function performs checks for rgba_to_int
        arguments and call it.

        >>> Colors.safe_rgba_to_int('rgba(255, 0, 150, 0.5)')
        (255, 0, 150)
        >>> Colors.safe_rgba_to_int('rgba(0.5)')
        (5, 0, 0)
        >>> Colors.safe_rgba_to_int('azerty | qwe255, rty1500, 0.2 |')
        (255, 220, 2)
        >>>
        """

        color_ = "rgba("
        counter = 0
        temp_color = ""
        for char in color:
            if char in "0123456789":
                temp_color += char

            if char == ",":
                counter += 1
                color_ += str(int(temp_color) % 256) + ", "
                temp_color = ""

                if counter == 3:
                    break

        if temp_color:
            counter += 1
            color_ += str(int(temp_color) % 256) + ", "

        while counter < 3:
            color_ += "0, "
            counter += 1

        return Colors.rgba_to_int(color_ + "0.5)")

    def rgba_to_int(colors: str) -> Tuple[int, int, int]:

        """
        This function translates RGBA (CSS function)
        colors to integers colors.

        >>> Colors.rgba_to_int('rgba(255, 0, 150, 0.5)')
        (255, 0, 150)
        >>>
        """

        return tuple(int(x) for x in colors.strip("rgba() ").split(",")[:3])

    def check_int_to_rgba(*args) -> str:

        """
        This function performs checks for int_to_rgba
        arguments and call it.

        >>> Colors.check_int_to_rgba(255, 0, 150, 0.5)
        'rgba(255, 0, 150, 0.5)'
        >>> Colors.check_int_to_rgba(256, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_rgba arguments should be int between 0 and 255 (256 is invalid).
        >>> Colors.check_int_to_rgba(255, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_rgba arguments should be int between 0 and 255 (-1 is invalid).
        >>> Colors.check_int_to_rgba(255, 0, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_rgba arguments should be int between 0 and 255 ('invalid' is invalid).
        >>>
        """

        invalid = False
        for arg in args[:3]:
            if not isinstance(arg, int) or arg > 255 or arg < 0:
                invalid = True
                break

        if invalid or (
            len(args) > 3
            and (
                not isinstance(args[3], float)
                or float(args[3]) > 1
                or float(args[3]) < 0
            )
        ):
            raise ValueError(
                "Colors.int_to_rgba arguments should "
                f"be int between 0 and 255 ({arg!r} is invalid)."
            )

        return Colors.int_to_rgba(*args[:4])

    def safe_int_to_rgba(*args) -> str:

        """
        This function performs checks for int_to_rgba
        arguments and call it.

        >>> Colors.safe_int_to_rgba(255, 0, 150)
        'rgba(255, 0, 150, 1)'
        >>> Colors.safe_int_to_rgba(256, -1, "invalid", 1.9)
        'rgba(0, 255, 0, 0.9)'
        >>>
        """

        args_ = []
        append = args_.append
        for i, arg in enumerate(args[:3]):
            if not isinstance(arg, int):
                arg = 0
            else:
                arg = arg % 256

            append(arg)

        if len(args) > 3:
            transparency = args[3]

            if isinstance(transparency, float):
                append(
                    float(
                        Decimal(str(transparency))
                        - Decimal(str(int(transparency)))
                    )
                )

        return Colors.int_to_rgba(*args_)

    def int_to_rgba(
        red: int, green: int, blue: int, transparency: float = 1
    ) -> str:

        """
        This function translates integers
        colors to RGBA (CSS function) colors.

        >>> Colors.int_to_rgba(255, 0, 150)
        'rgba(255, 0, 150, 1)'
        >>>
        """

        return f"rgba({red}, {green}, {blue}, {transparency})"

    def check_int_to_rgb(*args) -> str:

        """
        This function performs checks for int_to_rgb
        arguments and call it.

        >>> Colors.check_int_to_rgb(255, 0, 150)
        'rgb(255, 0, 150)'
        >>> Colors.check_int_to_rgb(256, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_rgb arguments should be int between 0 and 255 (256 is invalid).
        >>> Colors.check_int_to_rgb(255, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_rgb arguments should be int between 0 and 255 (-1 is invalid).
        >>> Colors.check_int_to_rgb(255, 0, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.int_to_rgb arguments should be int between 0 and 255 ('invalid' is invalid).
        >>>
        """

        for arg in args:
            if not isinstance(arg, int) or arg > 255 or arg < 0:
                raise ValueError(
                    "Colors.int_to_rgb arguments should "
                    f"be int between 0 and 255 ({arg!r} is invalid)."
                )

        return Colors.int_to_rgb(*args)

    def safe_int_to_rgb(*args) -> str:

        """
        This function performs checks for int_to_rgb
        arguments and call it.

        >>> Colors.safe_int_to_rgb(255, 0, 150)
        'rgb(255, 0, 150)'
        >>> Colors.safe_int_to_rgb(256, -1, "invalid")
        'rgb(0, 255, 0)'
        >>>
        """

        args_ = []
        append = args_.append
        for i, arg in enumerate(args):
            if not isinstance(arg, int):
                arg = 0
            else:
                arg = arg % 256

            append(arg)

        return Colors.int_to_rgb(*args_)

    def int_to_rgb(red: int, green: int, blue: int) -> str:

        """
        This function translates integers
        colors to RGB (CSS function) colors.

        >>> Colors.int_to_rgb(255, 0, 150)
        'rgb(255, 0, 150)'
        >>>
        """

        return f"rgb({red}, {green}, {blue})"

    def check_get_8bits_color(*args) -> int:

        """
        This function performs checks for get_8bits_color
        arguments and call it.

        >>> Colors.check_get_8bits_color(7, 7, 3)
        255
        >>> Colors.check_get_8bits_color(255, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.get_8bits_color the first two arguments should be int between 0 and 7 and the third should be int between 0 and 4 (255 is invalid).
        >>> Colors.check_get_8bits_color(6, -1, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.get_8bits_color the first two arguments should be int between 0 and 7 and the third should be int between 0 and 4 (-1 is invalid).
        >>> Colors.check_get_8bits_color(6, 0, "invalid")
        Traceback (most recent call last):
                ...
        ValueError: Colors.get_8bits_color the first two arguments should be int between 0 and 7 and the third should be int between 0 and 4 ('invalid' is invalid).
        >>>
        """

        counter = 0
        for arg in args:
            if (
                not isinstance(arg, int)
                or arg < 0
                or (counter < 2 and arg > 7)
                or (counter > 2 and arg > 4)
            ):
                raise ValueError(
                    "Colors.get_8bits_color the first two arguments should "
                    "be int between 0 and 7 and the third should be int "
                    f"between 0 and 4 ({arg!r} is invalid)."
                )

        return Colors.get_8bits_color(*args)

    def safe_get_8bits_color(*args) -> int:

        """
        This function performs checks for get_8bits_color
        arguments and call it.

        >>> Colors.safe_get_8bits_color(7, 7, 3)
        255
        >>> Colors.safe_get_8bits_color(255, 150, "abc")
        248
        >>>
        """

        args_ = []
        append = args_.append
        counter = 0
        for i, arg in enumerate(args):
            if not isinstance(arg, int):
                arg = 0
            elif counter < 2:
                arg = arg % 8
            else:
                arg = arg % 4

            counter += 1
            append(arg)

        return Colors.get_8bits_color(*args_)

    def get_8bits_color(red: int, green: int, blue: int) -> int:

        """
        This function returns integer (0-255) representing 8bits-1byte colors.

        >>> Colors.get_8bits_color(7, 7, 3)
        255
        >>> Colors.get_8bits_color(0, 0, 0)
        0
        >>>
        """

        return (red << 5) + (green << 2) + blue


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
