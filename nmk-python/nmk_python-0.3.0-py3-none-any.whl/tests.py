import shutil
import subprocess
import sys

from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig


class PytestBuilder(NmkTaskBuilder):
    def build(self, pytest_args: str):
        # Clean outputs
        for p in self.outputs:
            if p.is_dir():
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()

        # Invoke pytest
        subprocess.run([sys.executable, "-m", "pytest"] + pytest_args.split(" "), check=True, cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value)
