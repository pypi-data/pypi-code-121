import shutil
from pathlib import Path

from nmk.model.builder import NmkTaskBuilder


class CleanBuilder(NmkTaskBuilder):
    def build(self, path: str):
        # Check path
        to_delete = Path(path)
        if to_delete.is_dir():
            # Clean it
            self.logger.debug(f"Cleaning folder: {to_delete}")
            shutil.rmtree(to_delete)
        else:
            # Nothing to clean
            self.logger.debug(f"Nothing to clean (folder not found: {to_delete})")


class OutputMkdir(NmkTaskBuilder):
    def build(self):
        # Create output directory
        self.main_output.mkdir(parents=True, exist_ok=True)
