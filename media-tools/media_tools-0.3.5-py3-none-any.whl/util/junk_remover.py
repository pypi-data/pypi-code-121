import re
from pathlib import Path
from typing import List

from .base_filename_cleaner import BaseFilenameCleaner
from .command import Command, Commands, Move
from .util import find_files


class JunkRemover(BaseFilenameCleaner):

    JUNK_TO_REMOVE = {
        ' $': '',     # space(s) at beginning and before ".mp3"
        '-$': '',     # "-.mp3", " - .mp3"
        '^-': '',     # dash at beginning
        '^ ': '',     # space at beginning
        r'^\.': '',   # dot at beginning
        '--': '-',    # --
        '- -': '-',   # stray double dashes
        '_': ' ',     # underscores
        '-,': '-',    # dash before comma (BECAUSE THAT HAPPENS AND IT FUCKS EVERYTHING UP JFC)
        r' -(\S)': r' - \1',  # immediately leading dash with space before
        r'(\S)- ': r'\1 - ',  # immediately trailing dash with space after
        '  ': ' ',    # double spaces
        ' ,': ',',    # space before comma
        r'\[\]': '',
        r'\(\)': '',
    }

    def fix_commands(self) -> Commands:
        def has_junk(filename: Path) -> bool:
            return self.is_music_file(filename) and \
                any(re.search(s, self.filename_base(filename)) for s in self.JUNK_TO_REMOVE)

        mismatches = sorted(find_files(self._base_directory, has_junk))
        return [self.fix_command_for_file(mismatch) for mismatch in mismatches]

    def fix_command_for_file(self, mismatch: Path) -> Command:
        root = mismatch.parent
        fixed = self.filename_base(mismatch)
        extension = mismatch.suffix
        matches: List[str] = []
        changed = True
        while changed:
            changed, fixed = self._remove_some_junk(fixed, matches)
        return Move(mismatch, root.joinpath(fixed + extension), matches)

    def _remove_some_junk(self, fixed: str, matches: List[str]):
        changed = False
        for search, replace in self.JUNK_TO_REMOVE.items():
            new_fixed = re.sub(search, replace, fixed)
            if new_fixed != fixed:
                changed = True
                matches.append(search)
            fixed = new_fixed
        return changed, fixed
