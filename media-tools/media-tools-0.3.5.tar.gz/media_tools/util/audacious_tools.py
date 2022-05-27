__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import os
from subprocess import check_output
from typing import List, Optional
from urllib.parse import unquote

DEFAULT_AUDACIOUS_CONFIG_DIR = os.path.join(
    os.environ['HOME'], '.config', 'audacious'
)


class AudaciousTools:
    """Tools for working with the audacious media player"""

    PLAYLIST_DIR_NAME = 'playlists'
    PLAYLIST_EXTENSION = '.audpl'
    FILE_LINE_PREFIX = 'uri=file://'

    def __init__(
            self, base_config_dir: str = DEFAULT_AUDACIOUS_CONFIG_DIR, file_base_dir: str = '.'
    ) -> None:
        """
        :param base_config_dir: Directory containing the audacious configuration
        """
        self._base_directory = base_config_dir
        self._playlist_dir = find_first_dir(self.PLAYLIST_DIR_NAME, self._base_directory)
        self._file_base_dir = file_base_dir

    def get_currently_playing_playlist_id(self) -> str:
        order = self.get_playlist_order()
        return order[AudaciousTools._currently_playing_playlist_number() - 1]

    def get_playlist_order(self) -> List[str]:
        """All playlist ids for this audacious instance, sorted in tab order"""
        with open(self._playlist_order_file_path(), encoding='utf-8') as order_file:
            return order_file.readlines()[0].split(' ')

    @property
    def playlist_directory(self) -> str:
        """Directory where the playlists are for this audacious instance"""
        return self._playlist_dir

    def files_in_playlist(self, playlist_id: str, existing_only: bool = False) -> List[str]:
        """
        :param playlist_id: Playlist ID (filename)
        :param existing_only: only return files that exist in filesystem
        :return: All actually existing files in that playlist
        """
        lines = self._read_playlist(playlist_id)
        files = self._file_entries(lines)
        return existing_files(files) if existing_only else files

    def get_files_to_copy(self, number: int, playlist_id: str) -> List[str]:
        files_to_copy = self.files_in_playlist(playlist_id)
        return files_to_copy[:number] if number else files_to_copy

    def get_existing_files(self, number: int, playlist_id: str) -> List[str]:
        files_to_copy = self.files_in_playlist(playlist_id, existing_only=True)
        return files_to_copy[:number] if number else files_to_copy

    def _playlist_order_file_path(self) -> str:
        return os.path.join(self.playlist_directory, 'order')

    def _read_playlist(self, playlist_id: str) -> List[str]:
        with open(self._playlist_file_path(playlist_id), encoding='utf-8') as playlist_file:
            return playlist_file.readlines()

    def _playlist_file_path(self, playlist_id: str) -> str:
        return os.path.join(
            self.playlist_directory, playlist_id + AudaciousTools.PLAYLIST_EXTENSION
        )

    def _file_entries(self, lines: List[str]) -> List[str]:
        return [
            os.path.join(
                self._file_base_dir, unquote(line[len(AudaciousTools.FILE_LINE_PREFIX):]).strip()
            )
            for line in lines if line.startswith(AudaciousTools.FILE_LINE_PREFIX)
        ]

    @staticmethod
    def _currently_playing_playlist_number() -> int:
        return int(check_output(['audtool', 'current-playlist']))


def find_first_dir(name: str, path: str) -> Optional[str]:
    for root, dirs, _ in os.walk(path):
        if name in dirs:
            return os.path.join(root, name)
    return None


def existing_files(files: List[str]) -> List[str]:
    return [file for file in files if os.path.isfile(file)]
