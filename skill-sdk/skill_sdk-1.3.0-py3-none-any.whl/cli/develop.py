#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "develop" command"""

#
#   - starts skill-designer
#   - starts skill in development mode
#   - displays skill logs in "Test -> log output"
#   - modifies Python sources in "Design"
#

import os
import argparse
import logging
import pathlib
from contextlib import closing

import uvicorn

from skill_sdk.cli import (
    add_env_file_argument,
    add_module_argument,
    import_module_app,
    process_env_file,
    DEFAULT_MODULE,
)

logger = logging.getLogger(__name__)


def execute(arguments):
    """
    Run the app in "development" mode:

        set logging level to DEBUG
        logging format to human-readable
        override debug flag from configuration
        initialize Designer UI

    :param arguments:
    :return:
    """
    from skill_sdk import config, log

    # Set "debug" mode to prevent installing check_credentials dependency
    os.environ["SKILL_DEBUG"] = "true"
    process_env_file(arguments)

    # Set default log level to DEBUG, if not explicitly overridden with "--verbose"/"--quiet"
    loglevel = getattr(arguments, "loglevel", None) or logging.DEBUG
    log.setup_logging(loglevel, config.FormatType.HUMAN)

    if arguments.module == DEFAULT_MODULE:
        create_if_missing(arguments.module)

    module, app = import_module_app(arguments.module)

    logger.info("Loaded app: %s", repr(app))
    logger.info("Loaded handlers: %s", list(app.intents))

    run_config = config.settings.http_config()
    logger.info("Starting app with config: %s", repr(run_config))

    with closing(app.develop()):
        uvicorn.run(app, **run_config)


def create_if_missing(module) -> None:
    """
    When `vs develop` is called from an empty project,
    "impl" folder does not exist and "import_module_app" fails with ModuleNotFoundError.

        We'll double check if "impl"/"impl.py" is missing and create an empty folder.

    :param module:
    :return:
    """
    module_path = pathlib.Path.cwd() / module
    if module_path.exists() or module_path.with_suffix(".py").exists():
        return

    logger.debug("Creating modules folder %s...", module_path)
    module_path.mkdir()


def add_subparser(subparsers):
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    run_parser = subparsers.add_parser(
        "develop",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts the skill in development mode.",
    )
    add_env_file_argument(run_parser)
    add_module_argument(run_parser)
    run_parser.set_defaults(command=execute)
