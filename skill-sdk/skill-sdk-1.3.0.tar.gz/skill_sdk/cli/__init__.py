#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: utility functions"""

import sys
import argparse
import logging
import importlib
import pathlib
from typing import Optional, Text, Tuple
from types import ModuleType

from skill_sdk import config, skill, Skill


#
# Default module (folder) for handler implementations:
#
#   if folder is missing, it will be created if skill is in "development" mode
#   (ran with `vs develop`)
#
DEFAULT_MODULE = "impl"


def add_logging_options(parser: argparse.ArgumentParser) -> None:
    """
    Add common logging argument parameters

    :param parser:
    :return:
    """
    logging_arguments = parser.add_argument_group("Logging options")

    logging_arguments.add_argument(
        "-v",
        "--verbose",
        help="Set logging to INFO.",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    logging_arguments.add_argument(
        "-vv",
        "--debug",
        help="Set logging to DEBUG.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    logging_arguments.add_argument(
        "-q",
        "--quiet",
        help="Set logging to ERROR.",
        action="store_const",
        dest="loglevel",
        const=logging.ERROR,
    )


def add_module_argument(
    parser: argparse.ArgumentParser,
    default: Optional[Text] = DEFAULT_MODULE,
) -> None:
    parser.add_argument("module", help="Run module", nargs="?", default=default)


def add_env_file_argument(
    parser: argparse.ArgumentParser,
    default: Optional[Text] = config.DOTENV_FILE,
) -> None:
    """
    Add env-file parameter argument:

    :param parser:
    :param default:
    :return:
    """
    parser.add_argument(
        "-e",
        "--env-file",
        default=default,
        help="Location of dotenv file.",
    )


def process_env_file(arguments):
    """
    Set .dotenv file location

    :param arguments:
    :return:
    """

    env_file = getattr(arguments, "env_file", None)
    if env_file is not None:
        config.Settings.Config.env_file = getattr(arguments, "env_file")


def import_module_app(import_from: Text) -> Tuple[ModuleType, Skill]:
    """
    Import application from python module or package

    :param import_from: module or package name, can be in following formats:
                        "app.py", "app:app" or "app_dir"

    :return:
    """
    module_str, _, app_str = import_from.partition(":")

    path = pathlib.Path(module_str)

    # Insert current directory to sys.path
    cwd = pathlib.Path("").absolute().__str__()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    if path.suffix == ".py":
        module = importlib.import_module(path.stem)
    elif path.is_dir():
        module = importlib.import_module(module_str)
        for _ in path.iterdir():
            if _.is_file() and _.suffix == ".py" and _.stem != "__init__":
                importlib.import_module("." + _.stem, _.parent.name)
            elif _.is_dir() and "__init__.py" in [f.name for f in _.iterdir()]:
                importlib.import_module("." + _.stem, _.parent.name)
    else:
        module = importlib.import_module(module_str)

    # Extract the name of application variable, if specified (`main:app`)
    app = getattr(module, app_str, None)
    # Create a default app, if not
    if app is None:
        app = skill.init_app()

    # Add link to the originating module
    # for source reloading and intent handler updates from UI
    if app.debug:
        setattr(app, "_module", module)

    # Return imported module and the application instance
    return module, app
