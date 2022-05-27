__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
import os.path
import re
from math import log10
from pathlib import Path
from shutil import copy2, SameFileError
from typing import List, Optional

from media_tools.util import AudaciousTools


class PlaylistCopier:
    def __init__(self, audacious: AudaciousTools, playlist_id: str) -> None:
        self.audacious = audacious
        self.playlist_id = playlist_id

    def copy_playlist(self, number: int, target: Path, renumber: bool = False) -> None:
        if not target.exists():
            target.mkdir()
        if not target.is_dir():
            raise ValueError(f"{target} is not a directory")
        playlist_id = self.playlist_id or self.audacious.get_currently_playing_playlist_id()
        copy_files(self.audacious.get_existing_files(number, playlist_id), target, renumber)

    def move_files_to_original_places(self, music_dir: Path = Path.home() / 'Music') -> None:
        playlist_id = self.playlist_id or self.audacious.get_currently_playing_playlist_id()
        for file in self.audacious.files_in_playlist(playlist_id):
            move_file(Path(file), music_dir)


def copy_files(filenames_to_copy: List[str], target_dir: Path, renumber: bool) -> None:
    for i, file in enumerate(filenames_to_copy):
        filename = os.path.basename(file)
        target_filename = renumber_file(filename, i + 1, len(filenames_to_copy)) if renumber \
            else filename
        logging.info("%s/%s: %s", i + 1, len(filenames_to_copy), target_filename)
        copy_file(Path(file), target_dir / target_filename)


def find_file_by_name(name: str, path: Path) -> Optional[Path]:
    all_files = sorted(path.rglob(name))
    return all_files[0] if all_files else None


def copy_file(file: Path, target: Path) -> None:
    if not file.exists():
        logging.warning('%s does not exist, skipping', file)
        return
    try:
        copy2(file, target)
    except SameFileError as error:
        logging.warning(str(error))


def renumber_file(filename: str, number: int, total: int) -> str:
    width = max(int(log10(total)) + 1, 2)
    return f"{number:0{width}d} - {strip_leading_numbers(filename)}"


def move_file(file: Path, music_dir: Path):
    if file.is_file():
        return
    target_dir = file.parent
    original_file = find_file_by_name(file.name, music_dir)
    if original_file is None:
        return

    files_to_move = [
        f.name for f in original_file.parent.iterdir() if f.is_file()
    ]
    logging.info('TO MOVE: %s %s %s', original_file, target_dir, files_to_move)

    target_dir.mkdir(exist_ok=True)
    for move in files_to_move:
        (original_file.parent / move).rename(target_dir / move)
        logging.warning(
            '        MOVING %s -> %s', original_file.parent / move, target_dir / move
        )
    original_file.parent.rmdir()


def strip_leading_numbers(filename: str) -> str:
    return re.sub(r'^\d+\s*[-.]?\d*\s*[-.]?\s*', '', filename)
