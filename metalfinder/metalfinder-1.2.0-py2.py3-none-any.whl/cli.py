#!/usr/bin/python3

"""
CLI arguments comprehension
"""

import os
import sys
import argparse

from datetime import date
from pathlib import Path
from xdg.BaseDirectory import xdg_cache_home

from . import __version__


def output_choices(fname):
    """Restrict the output extension choices"""
    extension = os.path.splitext(fname)[1][1:]
    choices = ['txt', 'json', 'atom']
    if extension not in choices:
        sys.exit(f"output '{fname}' doesn't end with a supported extension."
                 f"Choose from {*choices, }")
    if not os.path.isdir(Path(fname).parent):
        sys.exit(f"output '{fname}' is not a valid path.")
    return fname


def date_lint(mdate):
    """Verify date is ISO 8601 and exit nicely if not"""
    try:
        date.fromisoformat(mdate)
    except ValueError:
        sys.exit(f"max-date '{mdate}' does not follow ISO 8601 (YYYY-MM-DD) format.")
    if date.today() > date.fromisoformat(mdate):
        sys.exit(f"max-date '{mdate}' should not be ealier than today ({date.today()})")
    return mdate


def dir_lint(path):
    """Verify path is a valid directory and exit nicely if not"""
    if not os.path.isdir(path):
        if path == os.path.join(xdg_cache_home, 'metalfinder'):
            os.mkdir(path)
        else:
            sys.exit(f"Path '{path}' is not valid.")
    return path


def parse_args():  # pylint: disable=W0613
    """Parse the arguments"""
    example_text = '''example:
        metalfinder -d "/home/foo/Music" -o "/home/foo/metalfinder.atom" -l "Montreal" -b "foo"'''
    mf_cache_dir = os.path.join(xdg_cache_home, 'metalfinder')
    parser = argparse.ArgumentParser(prog='metalfinder',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__,
                                     epilog=example_text)
    parser.add_argument('-d', '--directory', type=dir_lint,
                        help='music directory to scan to create artist list')
    parser.add_argument('-o', '--output', type=output_choices,
                        required=True, help='path to the desired output file')
    parser.add_argument('-l', '--location', type=str, required=True,
                        help='name of the city to use when looking for concerts')
    parser.add_argument('-b', '--bit-appid', type=str,
                        help='Bandsintown App ID (API key). Optional when the'
                        ' METALFINDER_BIT_APPID environment variable is set.',
                        default=os.environ.get('METALFINDER_BIT_APPID'))
    parser.add_argument('-c', '--cache-dir', type=dir_lint,
                        default=mf_cache_dir,
                        help='path to the cache directory, default: %(default)s')
    parser.add_argument('-m', '--max-date', type=date_lint,
                        help='max date in YYYY-MM-DD format (ISO 8601)')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('--verbose', action='store_true',
                        help='run the program in verbose mode')
    args = parser.parse_args()
    if not args.bit_appid:
        parser.error("the following arguments are required: -b/--bit-appid")
    return args
