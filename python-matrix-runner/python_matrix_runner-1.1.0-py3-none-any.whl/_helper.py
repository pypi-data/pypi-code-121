# -*- coding: utf-8 -*-
import io
import logging

from contextlib import contextmanager
from enum import Enum
from fnmatch import fnmatch
from inspect import signature, Parameter
from typing import Tuple, Union, Any, AnyStr
from functools import reduce, partial


def colorize(msg):
    """Colorize a message string with ANSI colors.

    Args:
        msg: The message string containing color codes.

    Returns:
        Message with replaced color codes.
    """
    from colorlog.escape_codes import escape_codes  # pylint: disable=import-outside-toplevel
    msg += "%(reset)s"
    return msg % escape_codes


@contextmanager
def log_formatter(fmt):
    """Context manager for root log formatters.

    The formatter of all root handlers is temporarily
    replaced with the given one.

    Args:
         fmt: Log formatter to be used, temporarily.
    """
    old_formatter = {}
    for hnd in logging.root.handlers:
        old_formatter[hnd] = hnd.formatter
        hnd.formatter = fmt
    yield
    for hnd in logging.root.handlers:
        hnd.formatter = old_formatter[hnd]


def fnmatch_ex(value: Union[str, Tuple, Enum], pattern: str) -> bool:
    """Extended version of function fnmatch.fnmatch accepting Axis values.

    The value can one of
        str: The call is forwarded to fnmatch.
        Enum: The value associated with the enumerate is processed, recursively.
        tuple: fnmatch is called for all tuple members, any match is accepted.

    Args:
        value: Axis value to be matched against.
        pattern: fnmatch pattern to match.

    Returns:
        True if pattern matches value, False otherwise.

    Raises:
        TypeError if value is of unsupported type.
    """
    if isinstance(value, str):
        return fnmatch(value, pattern)
    if isinstance(value, Enum):
        return fnmatch_ex(value.value, pattern)
    if isinstance(value, tuple):
        return any(fnmatch_ex(v, pattern) for v in value)
    return fnmatch(str(value), pattern)


def join(value, delim: str = "|"):
    """Flatten an arbitrary Axis value to a simple string representation.

    For Enum values flatten is called recursively with the associated value.
    For tuples flatten is called recursively for all contained values. The
    resulting list is joined with ch.
    String values are returned unchanged.
    All other types are converted to String.

    Args:
        value: Value converted to string.
        delim: Character to be used to join collections.

    Returns:
        String representation of input value, tuples joined with ch.
    """
    if isinstance(value, Enum):
        return join(value.value, delim)
    if isinstance(value, tuple):
        return delim.join([join(v, delim) for v in value])
    if isinstance(value, str):
        return value
    return str(value)


def reduce_dict(value):
    """Reduce dict values, recursively.

    Args:
        value: Any value.

    Returns:
        Reduced dict or plain value.
    """
    if isinstance(value, dict):
        return reduce(lambda x, y: x + reduce_dict(y), value.values(), [])
    return value


def is_msys_cygwin_tty(stream):
    """Check if running on a MSYS/Cygwin TTY"""
    # https://github.com/tartley/colorama/pull/226
    # pylint: disable=import-outside-toplevel, invalid-name, missing-class-docstring, too-few-public-methods
    try:
        import msvcrt
        import ctypes
        import re
    except ImportError:
        return False

    if not hasattr(stream, "fileno"):
        return False

    if not hasattr(ctypes, "windll") or not hasattr(ctypes.windll.kernel32, "GetFileInformationByHandleEx"):
        return False

    try:
        fileno = stream.fileno()
    except io.UnsupportedOperation:
        return False
    handle = msvcrt.get_osfhandle(fileno)
    FileNameInfo = 2

    class FILE_NAME_INFO(ctypes.Structure):
        _fields_ = [('FileNameLength', ctypes.c_ulong),
                    ('FileName', ctypes.c_wchar * 40)]

    info = FILE_NAME_INFO()
    ret = ctypes.windll.kernel32.GetFileInformationByHandleEx(handle,
                                                              FileNameInfo,
                                                              ctypes.byref(info),
                                                              ctypes.sizeof(info))
    if ret == 0:
        return False

    msys_pattern = r"\\msys-[0-9a-f]{16}-pty\d-(to|from)-master"
    cygwin_pattern = r"\\cygwin-[0-9a-f]{16}-pty\d-(to|from)-master"
    return re.match(msys_pattern, info.FileName) is not None or \
           re.match(cygwin_pattern, info.FileName) is not None



class partial_with_inspect(partial):  # pylint: disable=invalid-name
    """Function object to bind a function to arguments.

    This subclass of functools.partial enhances the function object
    with inspect functionality.
    """

    def __new__(cls, func, /, *args, **keywords):
        self = super().__new__(cls, func, *args, **keywords)
        self._arg_cache = None
        return self

    @property
    def __name__(self):
        """The name of the wrapped function."""
        return self.func.__name__

    def __getattr__(self, item: AnyStr):
        """Dynamically provide named access to bound function arguments.

        Args:
            item: An argument name.

        Returns:
            Value bound to the argument.
        """
        if item in self.keywords:
            return self.keywords[item]

        index, kind = self._arg_index(item)
        if index is not None:
            if kind == Parameter.VAR_POSITIONAL:
                return self.args[index:]
            if kind == Parameter.VAR_KEYWORD:
                return self.keywords
            return self.args[index]
        raise AttributeError(f"'partial_with_inspect<{self.__name__}>' object has no attribute '{item}'")

    def _arg_index(self, item: AnyStr) -> Tuple[int, Any]:
        # pylint: disable=access-member-before-definition, attribute-defined-outside-init
        if not self._arg_cache:
            sig = signature(self.func)
            self._arg_cache = {k: (pos, sig.parameters[k].kind) for pos, k in enumerate(sig.parameters)}
        return self._arg_cache.get(item, (None, None))
