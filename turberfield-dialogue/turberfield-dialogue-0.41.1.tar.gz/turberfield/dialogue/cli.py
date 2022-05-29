#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import logging

from turberfield.dialogue.directives import Pathfinder
from turberfield.utils.logger import Logger

DEFAULT_PAUSE_SECS = 1.2
DEFAULT_DWELL_SECS = 0.3


def resolve_objects(args):
    folders = [
        Pathfinder.string_import(i, relative=False, sep=":")
        for i in args.folder
    ]
    references = Pathfinder.string_import(
        args.references, relative=False, sep=":"
    )
    return folders, references


def parser(descr=__doc__):
    rv = argparse.ArgumentParser(description=descr)
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number"
    )
    return rv

def add_common_options(parser):
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=Logger.Level.DEBUG, default=Logger.Level.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    return parser

def add_casting_options(parser):
    parser.add_argument(
        "--references", default="",
        help="Give an import path to a list of Python references."
    )
    parser.add_argument(
        "--folder", action="append",
        help="Give a sequence of import paths to SceneScript folders."
    )
    parser.add_argument(
        "--roles", type=int, default=1,
        help="The number of roles [1] permitted for each member of cast."
    )
    parser.add_argument(
        "--strict", action="store_true", default=False,
        help="Only perform fully-cast scene files.")
    return parser

def add_performance_options(parser):
    parser.add_argument(
        "--repeat", type=int, default=0,
        help="Repeat the performance [0] times."
    )
    parser.add_argument(
        "--pause", type=float, default=DEFAULT_PAUSE_SECS,
        help="Time in seconds [{0}] to pause after a line.".format(DEFAULT_PAUSE_SECS)
    )
    parser.add_argument(
        "--dwell", type=float, default=DEFAULT_DWELL_SECS,
        help="Time in seconds [{0}] to dwell on each word.".format(DEFAULT_DWELL_SECS)
    )
    return parser
