#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "run" command"""

import argparse
import logging
from contextlib import closing

import uvicorn

from skill_sdk.cli import (
    add_env_file_argument,
    add_module_argument,
    import_module_app,
    process_env_file,
)

logger = logging.getLogger(__name__)


def execute(arguments):
    """
    Initialize and run an app with "uvicorn" server

    :return:
    """
    from skill_sdk import config, log

    process_env_file(arguments)

    # Set default log level to WARNING, if not explicitly overridden with "--verbose"/"--debug"
    loglevel = getattr(arguments, "loglevel", None) or logging.WARNING
    log.setup_logging(loglevel)

    module, app = import_module_app(arguments.module)

    logger.info("Loaded app: %s", repr(app))

    if not app.intents:
        raise RuntimeError(
            "No intent handlers loaded. Check the log messages for import errors..."
        )

    logger.info("Loaded handlers: %s", list(app.intents))

    run_config = config.settings.http_config()

    logger.info("Starting app with config: %s", repr(run_config))

    with closing(app):
        uvicorn.run(app, **run_config)


def add_subparser(subparsers):
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    run_parser = subparsers.add_parser(
        "run",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts the skill in production mode.",
        description="Run the HTTP server as configured to handle requests.",
    )
    add_env_file_argument(run_parser)
    add_module_argument(run_parser)
    run_parser.set_defaults(command=execute)
