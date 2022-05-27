import sys
from typing import List

from nmk.model.builder import NmkTaskBuilder
from nmk.utils import run_with_logs


class BlackBuilder(NmkTaskBuilder):
    def build(self, src_folders: List[str], line_length: int):
        # Delegate to black
        run_with_logs([sys.executable, "-m", "black", "-l", str(line_length)] + src_folders, self.logger)

        # Touch output file
        self.main_output.touch()


class IsortBuilder(NmkTaskBuilder):
    def build(self, src_folders: List[str]):
        # Delegate to isort
        run_with_logs([sys.executable, "-m", "isort"] + src_folders, self.logger)

        # Touch output file
        self.main_output.touch()
