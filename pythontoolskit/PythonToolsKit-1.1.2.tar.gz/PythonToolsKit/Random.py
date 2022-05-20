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

>>> from Random import *
>>> get_random_strings()
'*=y%oHo!LX'
>>> get_random_strings()
'@5ILc8zmAo'
>>> get_random_strings(2)
'Pe'
>>> get_random_strings((2, 7))
'`kvS"\\'
>>> get_random_strings((2, 7))
'Lw#S5F'
>>> get_random_strings((2, 7))
'n=f'
>>> get_random_strings((2, 7), 2, separator="\x00")
'^n^G_$\x00`R:1Lq'
>>> get_random_strings((2, 7), 2, separator="\x00", secure=True)
'nc/A5Y&\x00)}GlbmH:u}'
>>> get_random_strings((2, 7), (2, 4), separator="\x00", secure=True, urlsafe=True)
'n3HlX_dP5UpOuA\x00Nv_tdoJjdcBRGA\x00bPZuDzmeqA\x00fFrbCxmCq5rOpXM'
>>> get_random_strings((2, 7), (2, 4), separator="\x00", secure=True, urlsafe=True, characters="abc")
'Maf7jFx6Rlc\x00yZeGaGkXkyI\x00Zs58Qzq26Ljv\x00wLztvfoC6GOL'
>>> get_random_strings((2, 7), (2, 4), separator=" ; ", secure=True, characters="abc")
'babccbaaab ; babaacaba ; aacabcc ; abaacabc'
>>> get_random_strings((2, 7), (2, 4), separator=" ; ", secure=True, letters=True)
'UpcGnFsca ; ioYxlGM ; HdAjYOBae ; oBNdWSZN'
>>> get_random_strings((2, 7), (2, 4), separator=" ; ", secure=True, alphanumeric=True)
'CWKOABTsU5 ; XHKWtvXFPm ; OXcLSIHm7 ; vYYrUoOeBm ; 3ytV7IRUCp'
>>> get_random_strings((2, 7), (2, 4), separator="\xff", secure=True, ascii=True)
"\x1e\n'\x1aL\x02\x10J<ÿ8\x10\n|\x11wl\x06ÿ9\x0e\x1a5LD$ÿl\x16\x06\x10_f~11"
>>> get_random_strings((2, 7), (2, 4), separator="", secure=True, latin1=True)
'aÆ\x89¾O|\x99\x92Úó§b\x0bMIa§[\x16C)lÊa\x84CÃUûGî\x90\x0f¦\x01á\x82´\x01æÀ#\x83\x94D\x08âmh'
>>> get_random_strings((2, 7), (2, 4), separator="", secure=True, check_strong=True)
"]YM~G_tV^ZOQ- -)2qSV$r%e%-8Q-_bfk-bkk-tV',d"
>>>
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

__all__ = ["get_random_strings"]

from string import (
    printable,
    ascii_letters,
    digits,
    ascii_lowercase,
    ascii_uppercase,
    punctuation,
)
from secrets import token_urlsafe, choice as secret_choice, randbelow
from typing import List, Tuple, Union
from collections.abc import Callable
from random import randint, choices


def get_number_function(
    numbers: Union[int, Tuple[int, int]], secure: bool = False
) -> Callable:

    """
    This function returns a function to get (random) number.
    """

    if isinstance(numbers, int):
        return lambda: numbers
    elif secure:
        diff = numbers[1] - numbers[0]
        return lambda: randbelow(diff) + numbers[1]
    else:
        return lambda: randint(*numbers)


def get_random_strings(
    length: Union[int, Tuple[int, int]] = 10,
    numbers: Union[int, Tuple[int, int]] = 1,
    separator: str = None,
    secure: bool = False,
    urlsafe: bool = False,
    characters: str = printable[:-5],
    letters: bool = False,
    alphanumeric: bool = False,
    ascii: bool = False,
    latin1: bool = False,
    check_strong: bool = False,
) -> Union[str, List[str]]:

    """
    This function generates random strings.
    """

    if letters:
        chars = ascii_letters
    elif alphanumeric:
        chars = ascii_letters + digits
    elif ascii:
        chars = bytes(range(127)).decode("ascii")
    elif latin1:
        chars = bytes(range(256)).decode("latin-1")
    else:
        chars = characters

    get_length = get_number_function(length, secure)
    get_numbers = get_number_function(numbers, secure)

    if secure:
        get_random_chars = lambda x: "".join(
            secret_choice(chars) for i in range(x)
        )
    else:
        get_random_chars = lambda x: "".join(choices(chars, k=x))

    if urlsafe:
        get_random_chars = token_urlsafe

    if numbers == 1:
        random_strings = get_random_chars(get_length())
    else:
        random_strings = (
            get_random_chars(get_length()) for x in range(get_numbers())
        )

    if separator is not None:
        random_strings = separator.join(random_strings)

    if check_strong:
        temp = "".join(random_strings)
        if (
            not any(c in temp for c in ascii_lowercase)
            or not any(c in temp for c in ascii_uppercase)
            or not any(c in temp for c in digits)
            or not any(c in temp for c in punctuation)
        ):
            return get_random_strings(
                length,
                numbers,
                separator,
                secure,
                urlsafe,
                characters,
                letters,
                alphanumeric,
                ascii,
                latin1,
                check_strong,
            )

    return random_strings
