# -*- coding: utf-8 -*-

from enum import Enum
from typing import Callable, Optional, AnyStr, Type

# patching colorama to work on msys/cygwin terminals
# https://github.com/tartley/colorama/issues/224

try:
    # noinspection PyUnresolvedReferences
    import colorama
except ImportError:
    pass
else:
    from ._helper import is_msys_cygwin_tty

    # noinspection SpellCheckingInspection
    isatty = colorama.ansitowin32.StreamWrapper.isatty
    colorama.ansitowin32.StreamWrapper.isatty = lambda x: isatty(x) or is_msys_cygwin_tty(x)

from ._helper import partial_with_inspect
from .axis import Axis
from .action import Action, ActionFunction
from .command import Command, Result, CommandFunction
from .filter import Filter, FilterFunction
from .report import ReportFilter, ConsoleReport, CropReport, TransformReport, JUnitReport, FileReport
from .runner import Runner, RunnerApplication
from .inspect import InspectRunner

__all__ = ['Axis', 'Action', 'Command', 'Result', 'Runner', 'RunnerApplication',
           'matrix_action', 'matrix_axis', 'matrix_command', 'matrix_filter',
           'main', 'ReportFilter', 'ConsoleReport', 'CropReport',
           'TransformReport', 'JUnitReport', 'InspectRunner', 'FileReport']


def matrix_axis(name: AnyStr, abbrev: Optional[AnyStr] = None, desc: Optional[AnyStr] = None) \
        -> Callable[[Type[Enum]], Type[Enum]]:
    """Decorator to create a matrix axis from a enum.

    Args:
        name: A unique (per Builder) Axis name.
        abbrev: A unique (per Builder) Axis abbreviation.
        desc: Descriptive text to document the intention of this Axis.
    """
    def _axis(cls: Type[Enum]) -> Type[Enum]:
        doc = cls.__doc__ if not desc else desc
        setattr(cls, "axis", Axis(name, abbrev, cls, doc))
        setattr(cls, "match", lambda v, p: v in cls.axis.lookup(p))
        setattr(cls, "__getitem__", cls.axis.tostring)
        setattr(cls, "__str__", cls.axis.tostring)
        return cls
    return _axis


def matrix_action(fn: ActionFunction) -> Action:
    """Decorator for ActionFunction"""
    act = Action(fn.__name__, fn, fn.__doc__)
    setattr(fn, "action", act)
    return act


def matrix_command(**kwargs) -> Callable[[CommandFunction], Callable[..., Command]]:
    """Decorator for a CommandFunction.

    The decorated function can take arbitrary arguments and needs to return
    a list of command line arguments, see popen.

    Args:
        kwargs: Arguments passed on to Command constructor
    """
    def _command(fn: CommandFunction) -> Callable[..., Command]:
        def _command_with_args(*args, **keywords):
            return Command(partial_with_inspect(fn, *args, **keywords), **kwargs)
        return _command_with_args
    return _command


def matrix_filter(fn: FilterFunction) -> Filter:
    """Decorator for FilterFunction"""
    return Filter(fn)


main = RunnerApplication  # pylint: disable=invalid-name
