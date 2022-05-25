"""
A small library for getting current path data for a script that imports
this library.
"""

__all__ = ("current_dir", "current_file", "current_dir_as_cwd", "CurrentPathError")


from contextlib import contextmanager
import inspect
import os
from pathlib import Path
import sys
from typing import Union


class CurrentPathError(Exception):
    """An exception raised from the current_path module."""


def _calling_module_current_file(depth: int = 2) -> Path:
    """A callable to get the current file path for the calling script, which is
    intended to be called in this module.

    For example, current_path can't be used within this module because it
    will point to the module itself.

    :raises CurrentPathError: Cannot find path for the script current_path was imported into.
    """

    index: int = 0

    inspecting_frame = inspect.currentframe()
    while index < depth:
        assert inspecting_frame, "Previous stack frame not found."
        inspecting_frame = inspecting_frame.f_back
        index += 1
    assert inspecting_frame, "Previous stack frame not found."
    return Path(inspecting_frame.f_code.co_filename).absolute()


def current_file() -> Path:
    """Returns the current file for the importing script."""
    return _calling_module_current_file()


def current_dir() -> Path:
    """Returns the current directory for the importing script."""
    return _calling_module_current_file().parent.absolute()


PathType = Union[str, os.PathLike]


@contextmanager
def current_dir_as_cwd(*path_segments: PathType):
    """
    Creates a context manager that temporarily changes current working directory
    to the importing library's directory.
    :keyword with_joined_path: Specifies path to join with importing module's current directory.
    """
    old_dir = Path(os.getcwd()).absolute()
    importing_file = _calling_module_current_file(depth=3)
    #  By using depth=3, it skips over the stack frame created by @contextmanager.
    new_dir = importing_file.parent.absolute().joinpath(*path_segments)
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


def _init():
    """
    Running init code block in function for ease of testing.
    """
    if __name__ == "__main__":
        raise CurrentPathError("current_path is only intended to be imported.")

    if not hasattr(sys, "_getframe") or inspect.currentframe() is None:
        raise CurrentPathError("This module relies on sys._getframe, which is not available for"
                               "the Python implementation in use.")


_init()
