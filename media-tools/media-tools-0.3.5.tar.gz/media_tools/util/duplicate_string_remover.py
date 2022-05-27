import logging
import re
from pathlib import Path
from typing import List

from .command import Commands, Move
from .base_filename_cleaner import BaseFilenameCleaner


class DuplicateStringRemover(BaseFilenameCleaner):

    def fix_commands(self, min_length: int, recurse: bool) -> Commands:
        fix_commands: Commands = []
        if recurse:
            subdirs = sorted([name for name in self._base_directory.iterdir() if name.is_dir()])
            for subdir in subdirs:
                cleaner = DuplicateStringRemover(self._base_directory.joinpath(subdir.name))
                fix_commands += cleaner.fix_commands(min_length, True)

        files = self.get_music_files()
        to_remove = self.longest_common_substring_in_filenames(files)
        to_remove = self._exclude_common_use_cases(to_remove)
        if min_length and len(to_remove) < min_length:
            return fix_commands
        logging.info('----    DIR: %s    ----    REMOVE: "%s"', self._base_directory, to_remove)
        new_commands = [Move(
            self._base_directory.joinpath(file),
            self._base_directory.joinpath(file.name.replace(to_remove, '')),
            [to_remove]
        ) for file in files]
        fix_commands += new_commands
        return fix_commands

    @staticmethod
    def longest_common_substring_in_filenames(data: List[Path]) -> str:
        return DuplicateStringRemover.longest_common_substring([f.name for f in data])

    @staticmethod
    def longest_common_substring(data: List[str]) -> str:
        if len(data) > 1 and data[0]:
            return DuplicateStringRemover.iterate_substrings(data, '')
        return ''

    @staticmethod
    def iterate_substrings(data: List[str], substr: str) -> str:
        for i in range(len(data[0])):
            substr = DuplicateStringRemover.check_remaining_strings_for_substrings(data, substr, i)
        return substr

    @staticmethod
    def check_remaining_strings_for_substrings(data: List[str], substr: str, i: int) -> str:
        for j in range(len(data[0]) - i + 1):
            if j > len(substr) and all(data[0][i:i + j] in x for x in data):
                substr = data[0][i:i + j]
        return substr

    @staticmethod
    def _exclude_common_use_cases(to_remove: str) -> str:
        if to_remove[:3] == ' - ':
            to_remove = to_remove[3:]
        if re.match(r'.*\.\w+$', to_remove):
            to_remove = re.sub(r'\.\w+?$', '', to_remove)
        if to_remove.endswith('-'):
            to_remove = to_remove[:-1]
        elif to_remove.startswith('-'):
            to_remove = to_remove[1:]
        return to_remove
