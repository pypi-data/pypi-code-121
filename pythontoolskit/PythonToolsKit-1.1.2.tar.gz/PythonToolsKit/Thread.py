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

>>> from time import sleep
>>> def sleep_and_print(time=2, text="end"): sleep(time) or print(text)
...
>>> SimpleThread(sleep_and_print, 3, text="Hello World")
>>> @threadify
... def sleep_and_print(time=2, text="end"): sleep(time) or print(text)
...
>>> sleep_and_print()
>>> join_all()
end
Hello World
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

__all__ = ["SimpleThread", "threadify", "join_all"]

from threading import (
    Thread,
    enumerate as get_threads,
    current_thread,
    main_thread,
)
from collections.abc import Callable
from functools import wraps


class SimpleThread(Thread):

    """
    This class implements a simple Thread calls.
    """

    def __init__(self, function: Callable, *args, **kwargs):
        Thread.__init__(self, target=function, args=args, kwargs=kwargs)
        self.start()


def threadify(function: Callable) -> Callable:

    """
    This decorator implements a simple way to
    call a function in a new thread.
    """

    @wraps(function)
    def wrapper(*args, **kwargs) -> SimpleThread:

        return SimpleThread(function, *args, **kwargs)

    return wrapper


def join_all():

    """
    This function get all threads and join it.

    The current thread and the main thread are exclude.
    """

    thread_current = current_thread()
    thread_main = main_thread()

    for thread in get_threads():
        if thread is not thread_current and thread is not thread_main:
            thread.join()
