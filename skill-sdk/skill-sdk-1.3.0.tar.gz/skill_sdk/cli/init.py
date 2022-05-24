#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "init" command"""

import sys
import argparse
import pkg_resources
from pathlib import Path
from distutils.dir_util import copy_tree


def execute(args: argparse.Namespace) -> None:
    """
    Initialize an empty skill project

    :param args:
    :return:
    """
    import questionary

    # Projects folder path
    path = Path(
        args.out
        if args.out is not None
        else questionary.path(
            "Enter a path to create your project [default: '.']", only_directories=True
        ).ask()
    ).resolve()

    if not path.is_dir():
        exit(f"{repr(path)} not found.")

    #
    # Intent handlers are by default in "impl" folder,
    # if the folder exists, we have to ask user's permission to overwrite it
    #
    if (path / "impl").exists():
        confirm = questionary.confirm(
            f'Project directory {repr(path / "impl")} exists. Overwrite?', default=True
        ).ask()
        if not confirm:
            sys.exit("Exiting...")

    scaffold_path = pkg_resources.resource_filename(__name__, "scaffold")
    copy_tree(scaffold_path.__str__(), path.__str__())
    print(f"Project initialized at {repr(path.absolute())}.")


def add_subparser(subparsers) -> None:
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    init_parser = subparsers.add_parser(
        "init",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Initialize a new project.",
        description="Initializes a project template, with sample 'SMALLTALK__GREETINGS' intent handler, "
        "configuration and unit tests are included.",
    )

    init_parser.add_argument(
        "--name",
        default="my-skill",
        help="Name of the skill.",
    )

    init_parser.add_argument(
        "--out",
        default=None,
        help="Directory to create the project.",
    )

    init_parser.set_defaults(command=execute)
