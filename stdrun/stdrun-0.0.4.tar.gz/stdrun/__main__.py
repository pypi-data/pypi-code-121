import sys
from argparse import ArgumentParser
from stdrun import Run
import colorama

RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"


def stdout_print(line):
    print(line, end="")


def stderr_print(line):
    print(f"{BOLD}{RED}{line}{RESET}", end="", file=sys.stderr)


def main():
    colorama.init()
    parser = ArgumentParser()
    parser.add_argument("command", nargs="+", help="command to be executed")
    args = parser.parse_args()
    exit_code = Run(args.command, stdout_print, stderr_print, shell=True)
    print(f"Exit code: {exit_code}")


if __name__ == "__main__":
    main()
