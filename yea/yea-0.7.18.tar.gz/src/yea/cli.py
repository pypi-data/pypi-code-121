"""Command line entrypoint."""

import argparse
import sys
from typing import Callable, List, Optional

from yea import __version__, context, runner


if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class CliArgs:
    """Typed command line arguments."""

    plugin_args: List[str]

    def __init__(self, args: argparse.Namespace):
        self.action: Literal["run", "list", "r", "l"] = args.action
        self.all: bool = args.all if hasattr(args, "all") else False
        self.debug: bool = args.debug
        self.docs_only: bool = args.docs_only
        self.dryrun: bool = args.dryrun
        self.func: Callable = args.func
        self.live: bool = args.live
        self.platform: Optional[str] = args.platform
        self.shard: Optional[str] = args.shard
        self.suite: Optional[str] = args.suite
        self.tests: Optional[List[str]] = args.tests
        self.plugin_args: list = args.plugin_args or []


def cli_list(yc: "context.YeaContext") -> None:
    print("Tests:")
    yc._args.action = "list"
    tr = runner.TestRunner(yc=yc)
    tests = tr.get_tests()
    test_ids = [len(t.test_id) for t in tests if t.test_id is not None]
    if None in test_ids:
        raise ValueError("Test ids must be set.")
    tlen = max(test_ids) if test_ids else 0
    for t in tests:
        print("  {:<{}s}: {}".format(t.test_id, tlen, t.name))
    tr.clean()


def cli_run(yc: "context.YeaContext") -> None:
    yc._args.action = "run"
    tr = runner.TestRunner(yc=yc)
    tr.run()


def cli() -> None:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="action", title="action", description="Action to perform")
    parser.add_argument("--debug", action="store_true", help="Print out extra debug info")
    parser.add_argument("--docs-only", help="Read tests from docstrings only", action="store_true")
    parser.add_argument("--dryrun", action="store_true", help="Do not do anything")
    parser.add_argument("--live", action="store_true", help="Run against real server")
    parser.add_argument("--shard", help="Specify testing shard")
    parser.add_argument("--suite", help="Specify testing suite")
    parser.add_argument("--platform", help="Specify testing platform")
    parser.add_argument("-p", "--plugin-args", action="append", help="Add plugin args")
    parser.add_argument("--version", help="Print version and exit", action="store_true")

    parse_list = subparsers.add_parser("list", aliases=["l"])
    parse_list.set_defaults(func=cli_list)
    parse_list.add_argument("tests", nargs="*")

    parse_run = subparsers.add_parser("run", aliases=["r"])
    parse_run.add_argument("-a", "--all", action="store_true", help="Run all")
    parse_run.add_argument("tests", nargs="*")
    parse_run.set_defaults(func=cli_run)
    args = parser.parse_args()

    if args.version:
        print(f"Yea {__version__}")
        sys.exit(0)

    if not args.action:
        parser.print_help()
        sys.exit(1)

    cli_args = CliArgs(args)
    yc = context.YeaContext(args=cli_args)
    args.func(yc)


if __name__ == "__main__":
    cli()
