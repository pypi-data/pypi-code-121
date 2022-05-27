"""Command line interface."""

import contextlib
from typing import List, Optional

from libcli import BaseCLI

from netflix.netflix import Netflix


class NetflixCLI(BaseCLI):
    """Command line interface."""

    config = {
        # distribution name, not importable package name
        "dist-name": "rlane-netflix",
    }

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.parser = self.ArgumentParser(
            prog=__package__,
            description="Print list of Titles, number of Seasons and total number of Episodes.",
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""

        self.parser.add_argument(
            "--seasons",
            action="store_true",
            help="list seasons and number of episodes",
        )

        self.parser.add_argument(
            "--episodes",
            action="store_true",
            help="list episodes; implies `--seasons`",
        )

        self.parser.add_argument(
            "--movies-only",
            action="store_true",
            help="print movies only",
        )

        self.parser.add_argument(
            "--series1-only",
            action="store_true",
            help="print series1 only",
        )

        self.parser.add_argument(
            "--series2-only",
            action="store_true",
            help="print series2 only",
        )

        arg = self.parser.add_argument(
            "file",
            default=Netflix.DEFAULT_DATA_FILE,
            metavar="FILE",
            nargs="?",
            help="read from `FILE`, use `-` for `stdin`",
        )
        self.add_default_to_help(arg)

    def main(self) -> None:
        """Command line interface entry point (method)."""

        netflix = Netflix(self.options)
        with contextlib.suppress(BrokenPipeError):
            netflix.print_report()


def main(args: Optional[List[str]] = None) -> None:
    """Command line interface entry point (function)."""
    return NetflixCLI(args).main()
