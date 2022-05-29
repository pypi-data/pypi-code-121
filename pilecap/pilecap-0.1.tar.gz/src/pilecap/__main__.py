from __future__ import annotations

import sys

from pilecap import cli


def main() -> None:
    cli.cli(sys.argv[1:])
