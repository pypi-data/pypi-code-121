'''Utilities for parsing and handling commandline arguments'''
import argparse
import logging
from pathlib import Path
import sys
import yaml

from clmgr.__version__ import get_versions


log = logging.getLogger("root")


def parse_args(args):
    # Create argument parser
    formatter_class = lambda prog: argparse.HelpFormatter(
        prog, max_help_position=100, width=200
    )
    parser = argparse.ArgumentParser(
        prog="copyrightmgr", formatter_class=formatter_class
    )

    # Configure commandline options
    parser.add_argument(
        "-c", "--config", help="configuration file", default="copyright.yml"
    )
    # TODO: add stdin support
    # TODO: add input file support
    parser.add_argument("-i", "--file", help="input file", metavar="FILE")
    parser.add_argument(
        "-d", "--dir", help="input directory", default=Path.cwd(), metavar="DIR"
    )
    parser.add_argument(
        "--region",
        help="Copyright search region; default=10",
        default=10,
        metavar="REGION",
    )
    parser.add_argument(
        "--header-length",
        help="Header length; default=80",
        default=80,
        metavar="HEADER_LENGTH",
    )
    parser.add_argument("--debug", help="Verbose logging", action="store_true")
    parser.add_argument("--version", help="Show version", action="store_true")

    # Parse Arguments
    return parser.parse_args(args)


def handle_version(args):
    '''Print the version number if --version argument is provided on commandline

    Parameters
    ----------
    args
        Parsed commandline arguments

    Returns
    -------
        None

    '''
    if args.version:
        print(get_versions()["version"])
        sys.exit()


def handle_debug(args, logger):
    '''Handle --debug commandline option

    Parameters
    ----------
    args
        Parsed commandline arguments
    '''
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)


def handle_config_file(args):
    config_file = Path(args.config).absolute()
    if not Path.exists(config_file):
        log.error(f"Unable to find configuration {config_file}")
        sys.exit()
    return config_file


# Validate Input Directory
# The input directory defaults to current working directory
# So when using this with stdin this validation will
# not cause any errors
def handle_input_dir(args):
    input_dir = Path(args.dir).absolute()
    if not Path.exists(input_dir):
        log.error(f"Input directory {input_dir} does not exists")
        sys.exit()
    return input_dir


def read_config(config_file):
    log.debug(f"Reading configuration from: {config_file}")
    with open(config_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)
