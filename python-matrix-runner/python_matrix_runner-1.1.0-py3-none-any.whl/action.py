# -*- coding: utf-8 -*-

import logging
import weakref

from functools import reduce
from inspect import signature
from typing import Callable, List, Iterator, Tuple, Union, AnyStr, Optional

import matrix_runner.preferences as prefs

from ._helper import colorize
from .command import Command, Result
from .config import Config
from .report import ReportFilter

ActionFunction = Callable[[Config, Optional[Result]], Iterator[Union[Command, Tuple]]]


class Action:
    """Wrapper class for a matrix runner actions function.
    """

    _instances = set()

    def __init__(self, name: AnyStr, fn: ActionFunction, desc: AnyStr = None):
        """Initialize a new runner Action.

        Args:
            name: The unique name to identify this Action.
            fn: The function
            desc: Descriptive text to document the intention of this Action.
        """
        self._name = name
        self._fn = fn
        self._get_summary = None
        self._desc = desc
        self._instances.add(weakref.ref(self))

    def __del__(self):
        self._instances.discard(weakref.ref(self))

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def __call__(self, config: Config) -> List[Result]:
        results = []
        params = [config]
        if len(signature(self._fn).parameters) >= 2:
            params += [results]
        cmds = self._fn(*params)
        try:
            for cmd in cmds:
                results.append(cmd())
        except RuntimeError as e:
            logging.error(e)
            logging.debug(e, exc_info=True)
            results.append(Result())
        return results

    def summary(self, fn: Callable[[List[Result]], str]) -> Callable[[List[Result]], str]:
        """Record custom summary function."""
        self._get_summary = fn
        return fn

    @classmethod
    def get_instances(cls) -> Iterator:
        """Retrieve all class instances."""
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    @property
    def name(self) -> str:
        """The unique name to identify this Action."""
        return self._name

    @property
    def desc(self) -> str:
        """Descriptive text to document the intention of this Action."""
        return self._desc

    def get_summary(self, results: List[Result]) -> str:
        """Create a summary for this action."""
        if not results:
            return colorize(f"%({prefs.summary_colors()['skip']})s(skip)")
        try:
            if all(r.success for r in results):
                if self._get_summary:
                    return colorize(self._get_summary(results))
                if any(isinstance(r.test_report, ReportFilter.Summary) for r in results):
                    results_with_reports = filter(lambda r: isinstance(r.test_report, ReportFilter.Summary), results)
                    report_summaries = map(lambda r: r.test_report.summary, results_with_reports)
                    passed, executed = reduce(lambda a, b: (a[0]+b[0], a[1]+b[1]), report_summaries, (0, 0))
                    if passed == executed:
                        color = prefs.summary_colors()['success']
                    else:
                        color = prefs.summary_colors()['unstable']
                    return colorize(f"%({color})s{passed}/{executed}")
                return colorize(f"%({prefs.summary_colors()['success']})ssuccess")
        except RuntimeError as e:
            logging.debug(e, exc_info=True)
            return colorize(f"%({prefs.summary_colors()['error']})sERROR")
        return colorize(f"%({prefs.summary_colors()['fail']})sFAILED")
