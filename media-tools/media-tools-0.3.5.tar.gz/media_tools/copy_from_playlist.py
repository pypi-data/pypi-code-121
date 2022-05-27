#!/usr/bin/env python3

__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from shutil import copy2
from sys import argv
from time import time
from typing import List

from media_tools.util import AudaciousTools, find_files
from media_tools.util.logging import setup_logging
from media_tools.util.playlist_copier import PlaylistCopier


def find_newer_than(base_path: str, seconds: int) -> List[Path]:
    return find_files(Path(base_path), lambda file: time() - os.path.getctime(file) < seconds)


def copy_newest_files(src_dir: str, target_dir: str, max_days: int) -> None:
    to_copy = sorted(find_newer_than(src_dir, max_days * 24 * 60 * 60))
    for i, file in enumerate(to_copy):
        basedir = file.parent
        target_subdir = str(basedir).replace(src_dir, '').split(os.path.sep)
        target_path = Path(target_dir).joinpath(*target_subdir)
        target_path.mkdir(exist_ok=True)
        logging.info("%s/%s %s", i + 1, len(to_copy), str(file).replace(src_dir, '').strip('/'))
        if not file.joinpath(target_path).is_file():
            copy_ignoring_errors(file, target_path)


def copy_ignoring_errors(file: Path, target_path: Path) -> None:
    try:
        copy2(file, target_path)
    except OSError:
        pass


def parse_commandline(args: List[str]) -> Namespace:
    parser = ArgumentParser(
        description="Copy the first N existing files of an audacious playlist to a target folder"
    )
    subparsers = parser.add_subparsers(help='Available subcommands:', dest='subparser')
    # workaround for python issue https://bugs.python.org/issue26510
    subparsers.required = True  # type: ignore

    parser_copy = subparsers.add_parser(
        'copy', help='Copy files on the playlist to a specified target folder'
    )
    parser_copy.add_argument(
        '-p', '--playlist', type=str,
        help='ID of the playlist to copy (default: currently playing)'
    )
    parser_copy.add_argument(
        '-n', '--number', default=0, type=int,
        help='First N files to copy from the playlist (default: all)'
    )
    parser_copy.add_argument(
        '-r', '--renumber', action='store_true',
        help='Rename files to have playlist position prepended to file name'
    )
    parser_copy.add_argument('target', type=str, help='Name of the target folder')

    parser_restore = subparsers.add_parser(
        'restore', help='Move files back to the place in the file system they have on the playlist'
    )
    parser_restore.add_argument(
        '-p', '--playlist', type=str,
        help='ID of the playlist to copy (default: currently playing)'
    )

    parser_copy_newest = subparsers.add_parser(
        'copy_newest', help="Copy the latest files to a specified location"
    )
    parser_copy_newest.add_argument(
        '--max-age', type=int, help='Copy files newer than this many days'
    )
    parser_copy_newest.add_argument(
        '-s', '--source', type=str,
        default=os.path.expanduser('~/Music'),
        help='Source directory. Default: ' + os.path.expanduser('~/Music')
    )
    parser_copy_newest.add_argument('target', type=str, help='Name of the target folder')

    parser.add_argument(
        '-v', '--verbose', action='store_true'
    )

    return parser.parse_args(args)


def main() -> None:
    opts = parse_commandline(argv[1:])
    setup_logging(opts)
    audacious = AudaciousTools()
    if opts.subparser == 'copy_newest':
        copy_newest_files(opts.source, opts.target, opts.max_age)
    elif opts.subparser == 'restore':
        copier = PlaylistCopier(audacious, opts.playlist)
        copier.move_files_to_original_places()
    elif opts.subparser == 'copy':
        copier = PlaylistCopier(audacious, opts.playlist)
        copier.copy_playlist(opts.number, opts.target, opts.renumber)
    else:
        logging.critical("what are you doing?")


if __name__ == '__main__':
    main()
