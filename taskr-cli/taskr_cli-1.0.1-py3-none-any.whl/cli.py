import argparse
import os
import sys

from .__version__ import version as VERSION
from .taskr import _Taskr


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="taskr", description="A small utility to run tasks"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show the version number"
    )
    parser.add_argument("-l", "--list", action="store_true", help="Show defined tasks")
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        default=False,
        help="Generate a template task file",
    )

    args, custom_args = parser.parse_known_args()

    if args.init:
        _Taskr.init()
        return

    if args.version:
        print(f"Running {VERSION}")
        return

    # Below actions needs an instance of taskr

    try:
        # Attempt to import from anywhere if in envs
        root = ""
        if "PYENV_DIR" in os.environ:
            root = os.environ["PYENV_DIR"]
        elif "TASKR_DIR" in os.environ:
            root = os.environ["TASKR_DIR"]

        sys.path.append(root)

        import tasks
    except ImportError:
        print("No valid tasks.py file found in current directory. Run 'taskr --init'")
        parser.print_help()
        sys.exit(1)

    Taskr = _Taskr(tasks)

    # Custom arguments take precedence
    if custom_args:
        # Custom task was passed, take it in
        task = custom_args.pop(0)
        # Ignore anything that looks like a normal arg, it shouldn't be here
        if task.startswith("-"):
            parser.print_help()
        else:
            # At this point, custom the target command,
            # tasks are arguments for custom
            Taskr.process(task, custom_args)

    # Start other commands
    elif args.list:
        Taskr.list()

    # No tasks passed, check if we have a default task
    elif Taskr.hasDefault():
        Taskr.default()

    # Finally print help
    else:
        parser.print_help()
