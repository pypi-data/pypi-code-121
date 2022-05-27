import os
import shutil
import sys
from typing import List

from nmk.model.builder import NmkTaskBuilder
from nmk.utils import run_with_logs


class FlakeBuilder(NmkTaskBuilder):
    def build(self, src_folders: List[str]):
        # Remove and create report folder
        if self.main_output.exists():
            shutil.rmtree(self.main_output)
        self.main_output.mkdir()

        try:
            # Delegate to flake8
            run_with_logs([sys.executable, "-m", "flake8"] + src_folders, self.logger)
        except Exception as e:
            # Fake touched output, to retrigger analysis on next run
            old_time = self.main_input.stat().st_mtime - 1
            os.utime(self.main_output, (old_time, old_time))

            # Finally raise the exception
            raise e

        # Touch output file
        self.main_output.touch()
