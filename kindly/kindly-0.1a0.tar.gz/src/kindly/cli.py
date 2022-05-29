import argparse
import ast
import functools
import itertools
import logging
import os
import pathlib
import shlex
import subprocess
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


def _find_upwards(start: pathlib.Path, name: str) -> pathlib.Path:
    for parent in itertools.chain([start], start.parents):
        path = parent / name
        if path.exists():
            return path
    raise FileNotFoundError


def _spec() -> Dict[str, Dict]:
    default_commands = {
        "check_format": {
            "cmds": [
                "isort --check setup.py src/ tests/",
                "black --check setup.py src/ tests/",
            ],
        },
        "fix_format": {
            "cmds": [
                "isort setup.py src/ tests/",
                "black setup.py src/ tests/",
            ],
        },
        "greet": {
            "help": "Say hello to",
            "nargs": 1,
            "func": lambda args: print(f"Hello {args.args[0].capitalize()}!"),
        },
    }
    try:
        kindly_pyi = _find_upwards(pathlib.Path.cwd(), "kindly.pyl")
        user_commands = ast.literal_eval(kindly_pyi.read_text())
    except FileNotFoundError:
        user_commands = {}
    return default_commands | user_commands


def _check_calls(
    cmds: Union[List[str], List[List[str]]], args: argparse.Namespace
) -> None:
    for cmd in cmds:
        _check_call(cmd, args)


def _check_call(cmd: Union[str, List[str]], args: argparse.Namespace) -> None:
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    try:
        extra_args = args.args
    except AttributeError:
        extra_args = []

    subprocess.check_call(cmd + extra_args)


def _parser(config: Dict[str, Dict]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    for name, spec in config.items():
        sub = subparsers.add_parser(
            name, help=spec.get("help", name.capitalize().replace("_", " "))
        )
        try:
            sub.add_argument("args", nargs=spec["nargs"])
        except KeyError:
            pass

        if "cmd" in spec:
            sub.set_defaults(func=functools.partial(_check_call, spec["cmd"]))
        elif "cmds" in spec:
            sub.set_defaults(func=functools.partial(_check_calls, spec["cmds"]))
        elif "func" in spec:
            sub.set_defaults(func=spec["func"])
        else:
            raise RuntimeError(
                "Expected one of (cmd, cmds, func) in spec " "but got neither"
            )

    return parser


def cli(args: List[str]) -> None:
    # noinspection PyUnresolvedReferences
    # pylint: disable=protected-access
    logging.basicConfig(level=logging._nameToLevel[os.environ.get("LEVEL", "WARNING")])
    parser = _parser(_spec())
    parsed = parser.parse_args(args)
    try:
        parsed.func(parsed)
    except subprocess.SubprocessError:
        parser.exit(1)
