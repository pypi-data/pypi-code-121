from argparse import Action, FileType, Namespace, ArgumentParser, SUPPRESS
from copy import copy
from dataclasses import dataclass
from typing import List, Type, Union, Optional, Any, TypeVar, Generic, Callable, Tuple, Iterable, Dict

from pkm.utils.commons import IllegalStateException
from pkm.utils.dicts import remove_none_values
from pkm.utils.seqs import seq

_T = TypeVar("_T")
_CommandHandler = Callable[[Namespace], None]


def with_extras(inner_action: str = "store") -> Type[Action]:  # support store and store_true
    class _WithExtras(Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if inner_action == 'store':
                setattr(namespace, self.dest, values)
            else:
                setattr(namespace, self.dest, True)

            namespace._extras_pending = self.dest

    return _WithExtras


class ExtrasAppender(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace._extras_pending:  # noqa
            raise IllegalStateException(f"no receiver for extra '{values}'")

        extras_list_name = f"{namespace._extras_pending}_extras"  # noqa
        if not (extras_map := getattr(namespace, extras_list_name, None)):
            setattr(namespace, extras_list_name, extras_map := {})

        for value in values:
            if '=' in value:
                k, d, v = value.partition('=')
                extras_map[k] = v
            else:
                extras_map[value] = True


@dataclass
class Arg(Generic[_T]):
    name_or_flags: Union[str, List[str]]
    action: Union[str, Type[Action], None] = None
    nargs: Union[int, str, None] = None
    const: Optional[Any] = None
    default: Optional[_T] = None
    type: Union[Callable[[str], _T], FileType, None] = None
    choices: Optional[Iterable[_T]] = None
    required: Optional[bool] = None
    help: Optional[str] = None
    metavar: Union[str, Tuple[str, ...], None] = None
    dest: Optional[str] = None
    version: Optional[str] = None


@dataclass
class Command:
    path: str
    args: Iterable[Arg]
    handler: _CommandHandler
    help: str
    kwargs: Dict[str, Any]


def command(path: str, *args: Arg, **kwargs):
    def _command(func: _CommandHandler) -> _CommandHandler:
        func.__command = Command(path, args, func, func.__doc__, kwargs)
        return func

    return _command


class SubParsers:
    def __init__(self, parser: ArgumentParser):
        self._parser = parser
        self._subparsers_holder = parser.add_subparsers()
        self._subparsers: Dict[str, SubParsers] = {}

    def add_command(self, cmd: Command) -> ArgumentParser:
        path = cmd.path.split()

        if not path:
            raise ValueError("path cannot be empty")

        sp = self
        for p in path[1:-1]:
            if not (nsp := sp._subparsers.get(p)):
                new_parser = sp._subparsers_holder.add_parser(p)
                nsp = sp._subparsers[p] = SubParsers(new_parser)
            sp = nsp

        parser = sp._subparsers_holder.add_parser(path[-1])
        if cmd.help:
            parser.description = cmd.help

        for arg in cmd.args:
            d = remove_none_values(copy(arg.__dict__))
            name_or_flags = d.pop('name_or_flags')
            if isinstance(name_or_flags, str):
                name_or_flags = [name_or_flags]

            parser.add_argument(*name_or_flags, **d)

        parser.set_defaults(func=cmd.handler)
        return parser


def create_args_parser(
        desc: str, commands: Iterable[Any],
        command_customizer: Callable[[ArgumentParser, Command], None] = lambda _1, _2: None
) -> ArgumentParser:
    main = ArgumentParser(description=desc)
    parser = SubParsers(main)

    def customize_command(cmd_parser: ArgumentParser, cmd: Command):
        cmd_parser.add_argument('-+', action=ExtrasAppender, help=SUPPRESS, nargs=1)
        command_customizer(cmd_parser, cmd)

    seq(commands) \
        .map_not_none(lambda it: getattr(it, "__command", None)) \
        .for_each(lambda it: customize_command(parser.add_command(it), it))

    # add special handling for extras
    original_parse_args = main.parse_args

    def parse_args(args: List[str]) -> Namespace:
        args_with_modified_extras = [f"-{a}" if a.startswith("+") else a for a in args]

        result = original_parse_args(args_with_modified_extras)
        if hasattr(result, "_extras_pending"):
            delattr(result, "_extras_pending")
        return result

    main.parse_args = parse_args
    return main
