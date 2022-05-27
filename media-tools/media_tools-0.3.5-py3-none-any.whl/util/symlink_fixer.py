import re
from pathlib import Path
from typing import List, Tuple, Dict

from .command import Command, Relink, Nothing, Commands
from .base_filename_cleaner import BaseFilenameCleaner
from .junk_remover import JunkRemover
from .numbering_fixer import NumberingFixer
from .util import find_potential_files


class SymlinkFixer(BaseFilenameCleaner):

    def fix_commands(self, undo_info: Dict[str, str]) -> Commands:
        symlinks = self.find_broken_symlinks_with_original_targets()
        return [self._fix_symlink(symlink, target, undo_info) for symlink, target in symlinks]

    def _fix_symlink(self, symlink: Path, old_target: Path, undo_info: Dict[str, str]) -> Command:
        to_try = self.patterns_to_try(old_target, undo_info)
        for file in to_try:
            filepath = Path(file)
            if filepath.is_file():
                return Relink(symlink, filepath)
        return Nothing()

    def find_broken_symlinks_with_original_targets(self) -> List[Tuple[Path, Path]]:
        return [(symlink, self.symlink_target(symlink)) for symlink in self.find_broken_symlinks()]

    def find_broken_symlinks(self) -> List[Path]:
        def is_broken_symlink(path: Path) -> bool:
            return path.is_symlink() and not path.is_file()

        return find_potential_files(self._base_directory, is_broken_symlink)

    @staticmethod
    def symlink_target(symlink: Path) -> Path:
        return symlink.resolve()

    def patterns_to_try(self, moved_file: Path, undo_info: Dict[str, str]) -> List[Path]:
        to_try = [Path(dest) for source, dest in undo_info.items() if str(moved_file) in source]

        junk = JunkRemover(self._base_directory)
        to_try.append(junk.fix_command_for_file(moved_file)[1])

        for file in [moved_file] + to_try:
            to_try += SymlinkFixer.check_file(file)

        return to_try

    @staticmethod
    def check_file(file: Path) -> List[Path]:
        to_try = []
        for pattern in NumberingFixer.PATTERNS_TO_FIX:
            match = re.match("(.*)/" + pattern, str(file))
            if match:
                fixed_filename = f"{match.group(1)}/{match.group(2)} - {match.group(3)}"
                to_try.append(Path(fixed_filename))
        return to_try
