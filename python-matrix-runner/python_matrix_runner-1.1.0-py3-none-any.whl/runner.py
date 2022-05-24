# -*- coding: utf-8 -*-

import inspect
import logging
import sys

from argparse import ArgumentParser, Action as ArgumentAction, Namespace
from itertools import product
from pathlib import Path
from types import GeneratorType
from typing import Union, Iterable, Mapping, List, MutableMapping

from allpairspy import AllPairs
from colorlog import ColoredFormatter
from tabulate import tabulate

import matrix_runner.preferences as prefs

from .action import Action
from .axis import Axis
from .command import Result
from .config import Config
from .filter import Filter
from ._helper import join, reduce_dict, log_formatter, colorize


class _AppendAxisValuesAction(ArgumentAction):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []
        if isinstance(values, Iterable):
            items.extend(values)
        else:
            items.append(values)
        setattr(namespace, self.dest, items)


class LogFormatter(ColoredFormatter):
    """Custom log formatter"""

    class Record:
        """Custom log record carrying additional 'cmd' attribute."""

        def __init__(self, record):
            """Add attributes from the escape_codes dict and the record."""
            self.__dict__.update({'cmd': ''})
            self.__dict__.update(record.__dict__)

            # Keep a reference to the original record so ``__getattr__`` can
            # access functions that are not in ``__dict__``
            self.__record = record

        def __getattr__(self, name):
            return getattr(self.__record, name)

    def format(self, record):
        record = self.Record(record)
        return super().format(record)


class Slice:
    """Value class for slice fraction.
    """

    def __init__(self, value: str):
        self.numerator, self.denominator = [int(x) for x in value.split('/', 2)]
        if (self.numerator < 1) \
                or (self.denominator < 1) \
                or (self.numerator > self.denominator):
            raise ValueError()

    def __hash__(self):
        return hash((self.numerator, self.denominator))

    def __eq__(self, other):
        return ((hash(self) == hash(other)) or
                ((self.numerator == other.numerator) and
                (self.denominator == other.denominator)))


class Runner:
    """The matrix Runner base class.
    """

    def __init__(self):
        self._axes: MutableMapping[str, Axis] = {}
        self._actions: MutableMapping[str, Action] = {}
        self._filter = []
        self._args = None
        self._matrix = None
        self._records = {}

    @property
    def axes(self) -> Mapping[str, Axis]:
        """Dictionary of matrix configuration Axes used by this Runner."""
        return self._axes

    @property
    def actions(self) -> Mapping[str, Action]:
        """Dictionary of Actions provided by this Runner."""
        return self._actions

    def add_axis(self, axes: Union[Axis, Iterable[Axis]]) -> None:
        """Add Axes to the Runner matrix.

        Args:
            axes: Axis/axes to be added.

        Raises:
            TypeError if axis argument has inappropriate type.
            ValueError if an Axis with same name is already part of the matrix.
        """
        if isinstance(axes, GeneratorType):
            axes = list(axes)
        if isinstance(axes, Iterable) and all(isinstance(a, Axis) for a in axes):
            for axis in axes:
                self.add_axis(axis)
        elif isinstance(axes, Axis):
            if axes.name in self._axes:
                raise ValueError(f'Runner matrix already contains an Axis with name {axes.name}!')
            self._axes[axes.name] = axes
        else:
            raise TypeError(f'Parameter axis must be of type Axis not {str(type(axes))}!')

    def add_action(self, actions) -> None:
        """Add Action to the Runner

        Args:
            actions: Action(s) to be added

        Raises:
            TypeError if action argument is not of type Action.
            ValueError if action with same name already part of the configuration.
        """
        if isinstance(actions, GeneratorType):
            actions = list(actions)
        if isinstance(actions, Iterable) and all(isinstance(a, Action) for a in actions):
            for action in actions:
                self.add_action(action)
        elif isinstance(actions, Action):
            if actions.name in self._actions:
                raise ValueError(f'Runner matrix already contains an Action with name {actions.name}!')
            self._actions[actions.name] = actions
        else:
            raise TypeError(f'Parameter action must be of type Action not {str(type(actions))}!')

    @property
    def _arg_parser(self):
        """The ArgumentParser to run matrix configurations."""
        parser = ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--silent", action='store_true', help="Silent mode, only errors are shown.")
        group.add_argument("--verbose", action='store_true', help="Verbose log output.")
        group.add_argument("--debug", action='store_true', help="Debug log output.")
        parser.add_argument("--pairwise", "-2", action='store_true',
                            help="Reduce number of combinations using pairwise algorithm.")

        if "slice" in self._axes.keys():
            logging.warning("Axis slice shadows built-in --slice flag!")
        else:
            parser.add_argument("--slice", type=Slice, metavar='<HERE>/<TOTAL>',
                                help="Cut set of combinations into <TOTAL> number of slices "
                                     "and run ony <HERE>th one.")

        for axis in self._axes.values():
            flags = ["--" + axis.name]
            if axis.abbrev:
                flags += ["-" + axis.abbrev]
            parser.add_argument(*flags, type=axis.converter(), action=_AppendAxisValuesAction,
                                help=f"{axis.desc}: {', '.join([join(v) for v in axis])}")
        action_help = f"Action(s) to be executed: {', '.join(self._actions.keys())}"
        parser.add_argument("action", choices=list(self._actions.values()) + [[]], nargs='*',
                            metavar="action", type=self._actions.get, help=action_help)
        return parser

    def _parse_args(self, argv: List[str] = None) -> Namespace:
        """Parse the arguments using the ArgumentParser.
        The list of values for omitted matrix axes defaults to all possible values.

        Args:
            argv: List of command line arguments

        Returns:
            Namespace with all command line flags and arguments.
        """
        args = self._arg_parser.parse_args(argv)
        for axis in self._axes.values():
            if getattr(args, axis.name, None) is None:
                setattr(args, axis.name, axis.values)
        return args

    def run(self, argv: List[str] = None):
        """Run with given command line arguments."""
        args = self._parse_args(argv)

        if args.silent:
            logging.root.setLevel(logging.ERROR)
        if args.verbose:
            logging.root.setLevel(logging.INFO)
        if args.debug:
            logging.root.setLevel(logging.DEBUG)

        axes = []
        for axis in sorted(self._axes):
            axes.append([(axis, v) for v in getattr(args, axis)])
        if args.pairwise:
            self._matrix = [Config(**dict(m)) for m in
                            AllPairs(axes, filter_func=lambda row: not Filter.match(Config(**dict(row))))]
        else:
            self._matrix = [Config(**dict(m)) for m in product(*axes) if not Filter.match(Config(**dict(m)))]
        if isinstance(args.slice, Slice):
            if args.slice.denominator > len(self._matrix):
                logging.warning("Deviding %d combination into %d slices results in empty runs!",
                                len(self._matrix), args.slice.denominator)
            self._matrix = self._matrix[args.slice.numerator-1::args.slice.denominator]

        for config in self._matrix:
            self.run_config(args.action, config)
        return all(r.success for r in reduce_dict(self._records))

    def run_config(self, actions: List[Action], config: Config):
        """Run all actions for the given configuration."""
        for action in actions:
            cfg = "][".join([self._axes[k].tostring(vars(config)[k]) for k in sorted(self._axes.keys())])
            fmt = LogFormatter(f"%({prefs.prefix_colors()['config']})s[{cfg}]"
                               f"%({prefs.prefix_colors()['action']})s({action.name}"
                               f"%(cmd)s)%(reset)s %(log_color)s%(message)s")
            with log_formatter(fmt):
                results = action(config)
                self.record_results(action, config, results)

    def record_results(self, action: Action, config: Config, results: List[Result]):
        """Record execution results."""
        self._records_for(config)[action.name] = results

    def records_for(self, config: Config) -> Mapping[str, List[Result]]:
        """Retrieve all execution records for given config."""
        return dict(self._records_for(config))

    def _records_for(self, config: Config) -> MutableMapping[str, List[Result]]:
        config_dict = vars(config)
        records = self._records
        for k in sorted(config_dict.keys()):
            records = records.setdefault(config_dict[k], {})
        return records


class RunnerApplication(Runner):
    """Runner"""

    def __init__(self, argv=None, axes=None, actions=None):
        super().__init__()

        self._configure_logging()

        logging.root.setLevel(prefs.log_level())
        logging.root.updateColors(prefs.log_colors())  # pylint: disable=no-member

        script_dir = Path(inspect.stack()[-1][1]).resolve().parent
        work_dir = Path.cwd()
        if script_dir != work_dir:
            logging.error("====[ WARNING ]====")
            logging.error("The default Matrix Runner application expects the "
                          "script to be located in the current working "
                          "directory!")
            logging.error(colorize(f"Expected working directory: %(blue)s{script_dir}"))
            logging.error(colorize(f"Actual working directory: %(blue)s{work_dir}"))
            logging.error("===================")

        if axes is None:
            axes = Axis.get_instances()
        if actions is None:
            actions = Action.get_instances()
        self.add_axis(axes)
        self.add_action(actions)

        success = self.run(argv)
        self.summary()

        if not success:
            sys.exit(1)
        sys.exit(0)

    # noinspection SpellCheckingInspection
    @staticmethod
    def _configure_logging(level=logging.WARNING):
        fmt = ColoredFormatter("%(log_color)s%(message)s")

        stdouth = logging.StreamHandler(sys.stdout)
        stdouth.addFilter(lambda record: record.levelno <= logging.WARNING)
        stdouth.setFormatter(fmt)
        logging.root.addHandler(stdouth)

        stderrh = logging.StreamHandler(sys.stderr)
        stderrh.setFormatter(fmt)
        errfn = stderrh.setLevel
        stderrh.setLevel = lambda ll: errfn(ll) if ll >= logging.ERROR else errfn(logging.ERROR)
        logging.root.addHandler(stderrh)

        fn = logging.root.setLevel
        logging.root.setLevel = lambda l: (fn(l), stdouth.setLevel(l), stderrh.setLevel(l))
        logging.root.setLevel(level)

        type(logging.root).updateColors = lambda s, c: fmt.log_colors.update(c)

    def summary(self):
        """Write full execution summary to log."""
        headers = [colorize(f"%({prefs.prefix_colors()['config']})s{a}") for a in sorted(self._axes.keys())]
        headers += [colorize(f"%({prefs.prefix_colors()['action']})s{a}") for a in sorted(self._actions.keys())]
        rows = []
        for config in self._matrix:
            records = self.records_for(config)
            row = [
                colorize(f"%({prefs.summary_colors()['config']})s{self._axes[k].tostring(vars(config)[k])}")
                for k in sorted(self._axes.keys())
            ]
            row.extend([self._actions[k].get_summary(records.get(k)) for k in sorted(self._actions.keys())])
            rows.append(row)

        logging.warning("")
        logging.warning("Matrix Summary")
        logging.warning("==============")
        logging.warning("")
        logging.warning(tabulate(rows, headers=headers))
