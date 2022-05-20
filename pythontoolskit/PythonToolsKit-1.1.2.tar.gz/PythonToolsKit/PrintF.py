#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2021  Maurice Lambert

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

r"""
This package implements tools to build python package and tools.

>>> from PrintF import printf, ProgressBar
>>> printf("It's working !")
[+] It's working !
>>> printf("Is not working...", state="NOK")
[-] Is not working...
>>> printf("Oh no ! An exception is raised...", state="ERROR")
[!] Oh no ! An exception is raised...
>>> printf("It's running !", end="\n\n", state="INFO")
[*] It's running !

>>> printf("Please press enter to start the program...", start="\n", state="TODO")

[#] Please press enter to start the program...
>>> printf("Do you want to continue ?", pourcent=20, state="ASK"); print()
[?] Do you want to continue ?
[?] 20% |████                |
>>> printf("Step 1 OK", pourcent=20); printf("Step 2 OK", pourcent=55); print()
[+] Step 1 OK
[+] Step 2 OK
[+] 55% |███████████         |
>>> printf("Step 1 OK", pourcent=20); print(); printf("Step 2 OK", pourcent=55); print()
[+] Step 1 OK
[+] 20% |████                |
[+] Step 2 OK
[+] 55% |███████████         |
>>> printf("Step 2 OK", add_progressbar=False, pourcent=55); print()
[+] Step 2 OK
[+] 55%
>>> printf("Step 2 OK", oneline_progress=True, add_progressbar=False, pourcent=55); print()
[+] Step 2 OK 55%
>>> printf("Step 2 OK", oneline_progress=True, pourcent=55); print()
[+] Step 2 OK 55% |███████████         |
>>> import PrintF
>>> PrintF.STATES["TEST"] = ("[T]", "\x1b[37m")
>>> printf("Testing a custom state...", state="TEST")
[T] Testing a custom state...
>>> printf("Unknown", state="unknown")
[ ] Unknown
>>> custom_progress = ProgressBar("[", "]", "#", "-", 30)
>>> printf("Step 1 OK", progressbar=custom_progress, pourcent=20); print()
[+] Step 1 OK
[+] 20% [######------------------------]
>>>
"""

__version__ = "1.0.0"
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

__all__ = ["printf", "STATES"]

from sys import argv
from typing import Union
from platform import system
from dataclasses import dataclass


@dataclass
class ProgressBar:
    start: str = "|"
    end: str = "|"
    character: str = "\u2588"
    empty: str = " "
    size: int = 20


STATES = {
    "OK": ("[+]", "\x1b[32m"),
    "NOK": ("[-]", "\x1b[33m"),
    "ERROR": ("[!]", "\x1b[31m"),
    "INFO": ("[*]", "\x1b[34m"),
    "TODO": ("[#]", "\x1b[35m"),
    "ASK": ("[?]", "\x1b[36m"),
}

states_get = STATES.get


def printf(
    string: str,
    state: str = "OK",
    pourcent: int = None,
    start: str = "",
    end: str = "\n",
    progressbar: ProgressBar = ProgressBar,
    add_progressbar: bool = True,
    oneline_progress: bool = False,
    **kwargs,
) -> None:

    """
    This function prints formatted and colored information and progression.
    """

    show, color = states_get(state) or ("[ ]", "\x1b[39m")

    progress_bar = ""
    has_pourcent = pourcent is not None

    if has_pourcent and add_progressbar:
        max_size = progressbar.size
        char_size = 100 / max_size
        pourcent_size = round(pourcent / char_size)
        if pourcent_size > max_size:
            pourcent_size = max_size
        progress_bar = (
            progressbar.start
            + (progressbar.character * pourcent_size)
            + (progressbar.empty * (max_size - pourcent_size))
            + progressbar.end
        )

    if has_pourcent:
        progress_bar = f"{pourcent}% {progress_bar}\x1b[0m{end}\x1b[F"
        if not oneline_progress:
            progress_bar = f"{color}{show} {progress_bar}"

    if oneline_progress:
        to_print = f"\x1b[K{start}{color}{show} {string} {progress_bar}"
    else:
        to_print = (
            f"\x1b[K{start}{color}{show} {string}\x1b[0m{end}"
            f"{progress_bar}"
        )

    print(to_print, flush=True, end="", **kwargs)
