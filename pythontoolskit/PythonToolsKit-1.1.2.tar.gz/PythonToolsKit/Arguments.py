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

>>> from Arguments import *
>>> a = ArgumentParser()
>>> a.add_password()
(<argparse._MutuallyExclusiveGroup object at 0x00000204D515EA00>, _StoreAction(option_strings=['-p', '--password'], dest='password', nargs=None, const=None, default=None, type=None, choices=None, help=None, metavar=None), _StoreAction(option_strings=['-P', '--password-prompt'], dest='password_prompt', nargs=None, const=None, default=None, type=None, choices=None, help=None, metavar=None))
>>> a.add_input_file("-i")
_StoreAction(option_strings=['-i'], dest='i', nargs='?', const=<_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>, default=None, type=FileType('r'), choices=None, help=None, metavar=None)
>>> a.add_output_file("-o")
_StoreAction(option_strings=['-o'], dest='o', nargs='?', const=None, default=<_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>, type=FileType('w'), choices=None, help=None, metavar=None)
>>> a.add_verbose()
_StoreTrueAction(option_strings=['--verbose', '-v'], dest='verbose', nargs=0, const=True, default=False, type=None, choices=None, help='Active verbose mode.', metavar=None)
>>> a.add_debug()
_StoreTrueAction(option_strings=['--debug', '-d'], dest='debug', nargs=0, const=True, default=False, type=None, choices=None, help='Active debugging mode (set level debug for all loggers).', metavar=None)
>>>

>>> a = ArgumentParser(description="description")
>>> a.add_password(password_args=["-a", "--api-key"], prompt_args=["-A", "--api-key-prompt"], prompt_function=input, prompt_function_args="API Key:", password_kwargs={"help": "Help message"}, prompt_kwargs={"help", "Help message"}, mutually_group_kwargs={"required", True})
(<argparse._MutuallyExclusiveGroup object at 0x000001EC567EF730>, _StoreAction(option_strings=['-a', '--api-key'], dest='api_key', nargs=None, const=None, default=None, type=None, choices=None, help='Help message', metavar=None), _StoreAction(option_strings=['-A', '--api-key-prompt'], dest='api_key_prompt', nargs=None, const=None, default=None, type=None, choices=None, help='Help message', metavar=None))
>>> a.add_input_file("-i", "--input", file_args=["rb"], file_kwargs={"encoding": None}, help="Help message")
_StoreAction(option_strings=['-i', '--input'], dest='input', nargs='?', const=<_io.BufferedReader name='<stdin>'>, default=None, type=FileType('rb'), choices=None, help=None, metavar=None)
>>> a.add_output_file("-o", "--output", file_args=["wb"], file_kwargs={"encoding": None}, help="Help message")
_StoreAction(option_strings=['-o', '--output'], dest='output', nargs='?', const=None, default=<_io.BufferedWriter name='<stdout>'>, type=FileType('wb'), choices=None, help='Help message', metavar=None)
>>> a.add_verbose('-V', '--VERBOSE-MODE', function = print, help="Verbose mode.")
_StoreTrueAction(option_strings=['--VERBOSE-MODE', '-V'], dest='VERBOSE_MODE', nargs=0, const=True, default=False, type=None, choices=None, help='Verbose mode.', metavar=None)
>>> a.add_debug('-D', '--DEBUG-MODE', help="Debug mode.")
_StoreTrueAction(option_strings=['--DEBUG-MODE', '-d'], dest='DEBUG_MODE', nargs=0, const=True, default=False, type=None, choices=None, help='Debug mode', metavar=None)
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

__all__ = ["ArgumentParser", "verbose"]

from argparse import (
    ArgumentParser as _ArgumentParser,
    FileType,
    Namespace,
    _StoreAction,
    _MutuallyExclusiveGroup,
)
from logging import getLogger, root, basicConfig, DEBUG
from typing import List, Dict, Any, Tuple
from collections.abc import Callable
from sys import stdin, stdout
from functools import partial
from getpass import getpass
from inspect import stack

global verbose
verbose = lambda *x: None  # default do nothing (mode verbose not active)
vprint = partial(print, "[V]")


def set_verbose(verbose_function: Callable = vprint) -> None:

    """
    This function sets verbose mode.
    """

    global verbose

    module_caller_globals = stack()[
        2
    ].frame.f_globals  # 0: current, 1: parse_args, 2: call_parse_args

    if module_caller_globals.get("verbose") is verbose:
        module_caller_globals["verbose"] = verbose_function
    else:
        for key, value in module_caller_globals.items():
            if value is verbose:
                module_caller_globals[key] = verbose_function

    verbose = verbose_function


def set_debug() -> None:

    """
    This function sets log level for all loggers.
    """

    basicConfig(level=DEBUG)
    [getLogger(name).setLevel(DEBUG) for name in root.manager.loggerDict]


class ArgumentParser(_ArgumentParser):

    """
    argparse.ArgumentParser + preconfigured and commons arguments.
    """

    # _actions_ = {}

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.password_prompt_destination = None
        self.password_prompt_action = None
        self.verbose_destination = None
        self.debug_destination = None
        self.verbose_function = vprint

    def add_password(
        self,
        password_args: List[Any] = ["-p", "--password"],
        prompt_args: List[Any] = ["-P", "--password-prompt"],
        prompt_function: Callable = getpass,
        prompt_function_args: List[Any] = [],
        prompt_function_kwargs: List[Any] = {},
        password_kwargs: Dict[str, Any] = {},
        prompt_kwargs: Dict[str, Any] = {},
        mutually_group_kwargs: Dict[str, Any] = {},
    ) -> Tuple[_MutuallyExclusiveGroup, _StoreAction, _StoreAction]:

        """
        This function add password argument and password prompt
        arguments.
        """

        # max_prompt = max(prompt_args, key=lambda x: len(x))
        # for arg in prompt_args:
        #     self._actions_[arg] = (
        #         max_prompt,
        #         partial(
        #             prompt_function,
        #             *prompt_function_args,
        #             **prompt_function_kwargs,
        #         ),
        #     )

        password = self.add_mutually_exclusive_group()
        password_add_argument = password.add_argument

        arg1 = password_add_argument(
            *password_args,
            **password_kwargs,
        )
        arg2 = password_add_argument(
            *prompt_args,
            action="store_true",
            **password_kwargs,
        )

        self.password_prompt_destination = arg2.dest
        self.password_prompt_action = partial(
            prompt_function, *prompt_function_args, **prompt_function_kwargs
        )

        return password, arg1, arg2

    def add_input_file(
        self,
        *args,
        file_args: List[Any] = [],
        file_kwargs: Dict[str, Any] = {},
        **kwargs,
    ) -> _StoreAction:

        """
        This function add input file argument.

        By default if not present in the command line
        the value is None. If is present in the command line
        but no value follow use the stdin. If present with a
        value, the ArgumentParser will try to open the file.

        The function accepts the binary mode ("rb").
        """

        if (file_args and "b" in file_args[0]) or (
            "mode" in file_kwargs and "b" in file_kwargs["mode"]
        ):
            default = stdin.buffer
        else:
            default = stdin

        kwargs2 = {
            "nargs": "?",
            "const": default,
            "type": FileType(*file_args, **file_kwargs),
        }
        kwargs2.update(kwargs)

        return self.add_argument(*args, **kwargs2)

    def add_output_file(
        self,
        *args,
        file_args: List[Any] = ["w"],
        file_kwargs: Dict[str, Any] = {},
        **kwargs,
    ) -> _StoreAction:

        """
        This function add output file argument.

        By default if not present in the command line
        the value is stdout. If is present in the command line
        but no value follow use the stdout. If present with a
        value, the ArgumentParser will try to open the file.

        The function accepts the binary mode ("wb").
        """

        if (file_args and "b" in file_args[0]) or (
            "mode" in file_kwargs and "b" in file_kwargs["mode"]
        ):
            default = stdout.buffer
        elif file_args is None and "mode" not in file_kwargs:
            file_args[0] = "w"
            default = stdout
        else:
            default = stdout

        kwargs2 = {
            "nargs": "?",
            "default": default,
            "const": default,
            "type": FileType(*file_args, **file_kwargs),
        }
        kwargs2.update(kwargs)

        return self.add_argument(*args, **kwargs2)

    def add_verbose(
        self, *args, function: Callable = vprint, **kwargs
    ) -> _StoreAction:

        """
        This method adds verbose argument to the parser.
        """

        if not args:
            args = ["--verbose", "-v"]

        default_kwargs = {
            "default": False,
            "help": "Active verbose mode.",
            "action": "store_true",
        }

        default_kwargs.update(kwargs)

        argument = self.add_argument(*args, **default_kwargs)
        self.verbose_destination = argument.dest
        self.verbose_function = function

        return argument

    def add_debug(self, *args, **kwargs) -> _StoreAction:

        """
        This method adds debug argument to the parser.
        """

        if not args:
            args = ["--debug", "-d"]

        default_kwargs = {
            "default": False,
            "help": "Active debugging mode (set level debug for all loggers).",
            "action": "store_true",
        }

        default_kwargs.update(kwargs)

        argument = self.add_argument(*args, **default_kwargs)
        self.debug_destination = argument.dest

        return argument

    def parse_args(self, *args, **kwargs) -> Namespace:

        """
        This function parse command line arguments.
        """

        response = _ArgumentParser.parse_args(self, *args, **kwargs)

        password_prompt_destination = self.password_prompt_destination
        verbose_destination = self.verbose_destination
        debug_destination = self.debug_destination

        if password_prompt_destination is not None and getattr(
            self, password_prompt_destination, False
        ):
            setattr(
                self,
                password_prompt_destination,
                self.password_prompt_action(),
            )

        if verbose_destination is not None and getattr(
            response, verbose_destination, False
        ):
            set_verbose(self.verbose_function)

        if debug_destination is not None and getattr(
            response, debug_destination, False
        ):
            set_debug()

        # for arg, action in self._actions_.items():

        #     attribut, function = action
        #     attribut = attribut.lstrip("-").replace("-", "_")
        #     arg = arg.lstrip("-").replace("-", "_")

        #     if getattr(response, arg, False):
        #         setattr(response, attribut, function())

        return response


if __name__ == "__main__":
    a = ArgumentParser(description="description")
    a.add_password(
        password_args=["-a", "--api-key"],
        prompt_args=["-A", "--api-key-prompt"],
        prompt_function=input,
        prompt_function_args=["API Key: "],
        password_kwargs={"help": "Help message"},
        prompt_kwargs={"help", "Help message"},
        mutually_group_kwargs={"required", True},
    )
    a.add_input_file(
        "-i",
        "--input",
        file_args=["rb"],
        file_kwargs={"encoding": None},
        help="Help message",
    )
    a.add_output_file(
        "-o",
        "--output",
        file_args=["wb"],
        file_kwargs={"encoding": None},
        help="Help message",
    )
    print(a.parse_args(["-a", "apikey", "-i", "-o", "file.txt"]))
    print(a.parse_args(["-A", "-i", "file.txt", "-o"]))
    print(a.parse_args(["-a", "apikey", "-i", "file.txt"]))

    from os import remove

    remove("file.txt")

    print(a.parse_args())
    breakpoint()
