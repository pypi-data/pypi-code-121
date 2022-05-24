import argparse
import logging
import subprocess
import sys

import pkg_resources

from .allurectl import (ALLURECTL_VERSION, get_allure_executable,
                        get_platforms, install_allurectl)
from .logger import get_logger, set_level
from .testops import AllureTestops, get_available_actions

allurectl_version = ALLURECTL_VERSION.replace('.', '')
__version__ = '1.2.0.{}'.format(allurectl_version)

LOGGER = get_logger()


def get_default_parser(prog: str = None):
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument('-p', '--platform',
                        help='platform for allurectl execuatble binary',
                        dest='platform',
                        choices=['auto'] + get_platforms(),
                        default='Linux.i386')
    parser.add_argument('-v', '--verbose',
                        help='increase output verbosity',
                        action='store_true')
    return parser


def run_allurectl() -> None:
    parser = get_default_parser()
    parsed_args, unknown = parser.parse_known_args()

    install_allurectl(parsed_args.platform)
    command = [pkg_resources.resource_filename(
        'easy_allure',
        '/bin/{}'.format(get_allure_executable(parsed_args.platform)))
    ]

    command.extend(unknown)
    if parsed_args.verbose:
        set_level(logging.DEBUG)
        LOGGER.debug(command)

    subprocess.call(command)


def main():
    LOGGER.info('Running easy_allure v{}'.format(__version__))

    actions = get_available_actions()
    parser = get_default_parser(prog='easy_allure')

    parser.add_argument('action', choices=actions.keys())
    parser.add_argument('reports_path')
    parser.add_argument('-l', '--launch-name', dest='launch_name',
                        default='default_launch_name')

    parsed_args = parser.parse_args()
    if parsed_args.verbose:
        set_level(logging.DEBUG)

    testops_obj = AllureTestops(parsed_args.platform)
    try:
        sys.exit(actions[parsed_args.action](testops_obj, parsed_args))
    except Exception as err:
        LOGGER.error(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
