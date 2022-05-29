import sys

from kindly import cli


def main() -> None:
    cli.cli(sys.argv[1:])
