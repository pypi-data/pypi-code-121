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

>>> file = open("./configuration.conf")             # File should exist
>>> file.close()                                    # File should be closed
>>> file = open("./configuration.conf", "wb")       # File should exist
>>> file.write(b"my configuration")
>>> file.close()                                    # File should be closed
>>> filename = get_real_path("./data.db")           # File should exist, slower
>>> filename = get_real_path("./data.db", __FILE__) # File should exist, faster
>>> filename = get_real_path("./data.db", dirname(__FILE__)) # File should exist, faster
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

__all__ = ["get_real_path", "open"]

from os.path import normcase, join, isfile, dirname
from inspect import stack, getframeinfo
from io import TextIOWrapper
from platform import system
import builtins

system: str = system()


def get_real_path(file_path: str, module_path: str = None) -> str:

    """
    This function researchs a file from current
    directory and lib directory.
    """

    if file_path is None:
        return file_path

    if module_path is None:
        module_path = dirname(
            getframeinfo(stack()[1][0]).filename
        )  # precedent call
    elif isfile(module_path):
        module_path = dirname(module_path)

    if system == "Windows":
        length = 2
        index = 1
        character = ":"
    else:
        length = 1
        index = 0
        character = "/"

    file_path = normcase(file_path)
    module_file_path = join(normcase(module_path), file_path)

    if isfile(file_path):
        return file_path
    elif (
        len(file_path) > length
        and file_path[index] != character
        and isfile(module_file_path)
    ):
        return module_file_path

    raise FileNotFoundError(f"No such file or directory: '{file_path}'")


def open(file_path: str, *args, **kwargs) -> TextIOWrapper:

    """
    This function researchs a file from current
    directory and lib directory and open it.
    """

    return builtins.open(get_real_path(file_path), *args, **kwargs)
