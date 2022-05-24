#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "version" command"""

#
# Simply outputs the skill version as specified in config files:
#
#   this command is used in internal GitLab pipelines
#   to generate docker image name for the skill
#

import argparse
import logging

from skill_sdk.cli import (
    add_env_file_argument,
    add_module_argument,
    process_env_file,
)


def execute(arguments):
    """Print skill version"""

    from skill_sdk import config, log

    process_env_file(arguments)

    # Set default log level to ERROR, if not explicitly overridden with "--verbose"/"--debug"
    loglevel = getattr(arguments, "loglevel", None) or logging.ERROR
    log.setup_logging(loglevel, config.FormatType.HUMAN)

    # Reload setting from a config file
    config.settings.reload()

    print(config.settings.SKILL_VERSION)


def add_subparser(subparsers):
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    version_parser = subparsers.add_parser(
        "version",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Print skill version and exit.",
    )
    add_env_file_argument(version_parser)
    add_module_argument(version_parser)
    version_parser.set_defaults(command=execute)
