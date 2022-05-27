__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
import sys
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from datetime import timedelta
from functools import lru_cache
from operator import itemgetter
from os import get_terminal_size
from pathlib import Path
from pprint import pformat
from typing import List, Dict

import magic

from media_tools.util.length_reader import (
    AudioreadLengthReader, Eyed3LengthReader, MutagenLengthReader, SoundfileLengthReader
)
from media_tools.util.logging import setup_logging

AUDIO_EXTENSIONS = ('mp3', 'ogg', 'flac', 'wav', 'm4a', 'aif', 'aiff')


def parse_commandline(args: List[str]) -> Namespace:
    parser = ArgumentParser(
        description="Print length of audio files in directories"
    )
    parser.add_argument('directory', type=str, help='Directories to print')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--max-debug-items', type=int, default=-1, help='N shortest items to print')
    return parser.parse_args(args)


class LengthStore:

    def __init__(self, root: Path):
        self.root = root
        self.lengths: Dict[Path, timedelta] = {}
        self.errors: Dict[Path, float] = {}
        self.backends_used: Dict[str, Dict[Path, float]] = defaultdict(dict)

    def scan(self):
        self.lengths[self.root] = self.dir_length(self.root)

    def print_metadata(self, num_entries: int = -1):
        width, _ = get_terminal_size(0)
        logging.debug(pformat({
            backend: [
                f"{track.relative_to(self.root)}: {length:.1f}s"
                for track, length in sorted(tracks.items(), key=itemgetter(1))[:num_entries]
            ]
            for backend, tracks in self.backends_used.items()
        }, width=width))

    def print_errors(self, num_entries: int = -1):
        width, _ = get_terminal_size(0)
        logging.warning('%s errors', len(self.errors))
        logging.warning(pformat([
            f"{track.relative_to(self.root)}: {size / 1024:.1f}kB"
            for track, size in sorted(self.errors.items(), key=itemgetter(1))[:num_entries]
        ], width=width))

    @lru_cache(maxsize=100000)
    def dir_length(self, folder: Path) -> timedelta:
        length = timedelta(seconds=0)
        for thing in folder.iterdir():
            if is_audio(thing):
                try:
                    length += timedelta(seconds=self.get_duration(thing))
                except OverflowError:
                    pass
            elif thing.is_dir():
                duration = self.dir_length(thing)
                if duration:
                    self.lengths[thing] = duration
                    length += duration
        return length

    def print(self) -> None:
        max_duration = self.format_timedelta(self.lengths[self.root])
        for path, duration in sorted(self.lengths.items(), key=lambda item: item[1]):
            self.print_line(
                path if path == self.root else path.relative_to(self.root),
                self.format_timedelta(duration).rjust(len(max_duration))
            )

    @staticmethod
    def format_timedelta(duration: timedelta) -> str:
        days = duration.days
        rest = duration - timedelta(days=days)
        hours = str(rest).split('.', maxsplit=1)[0]
        return f"{days}d {hours:>8}" if days else hours

    @staticmethod
    def print_line(path: Path, duration: str) -> None:
        logging.info("%s   %s", duration, path)

    def get_duration(self, track: Path) -> float:
        for reader_class in (
                MutagenLengthReader, Eyed3LengthReader, SoundfileLengthReader, AudioreadLengthReader
        ):
            duration = reader_class(track).get_duration()
            if duration:
                self.backends_used[reader_class.__name__][track] = duration
                return duration
        self.errors[track] = track.stat().st_size
        return 0


def is_audio(track: Path):
    if not track.is_file():
        return False
    if track.suffix[1:].lower() in AUDIO_EXTENSIONS:
        return True
    file_magic = magic.from_file(str(track), mime=True)
    return file_magic.startswith('audio/')


def main() -> None:
    args: List[str] = sys.argv[1:]
    opts = parse_commandline(args)
    setup_logging(opts, fmt='%(message)s')
    lengths = LengthStore(Path(opts.directory))
    lengths.scan()
    lengths.print()
    if lengths.errors:
        lengths.print_errors(opts.max_debug_items)
    if opts.debug:
        lengths.print_metadata(opts.max_debug_items)


if __name__ == '__main__':
    main()
