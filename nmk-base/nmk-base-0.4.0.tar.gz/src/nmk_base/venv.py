import re
from pathlib import Path
from typing import List

from nmk.model.builder import NmkTaskBuilder
from nmk.utils import run_pip

from nmk_base.common import TemplateBuilder

# Pattern for pip list lines
PIP_LIST_PATTERN = re.compile("^([^ ]+) +([0-9][^ ]*)$")


class VenvRequirementsBuilder(TemplateBuilder):
    def build(self, file_deps: List[str], template: str):
        file_requirements = []

        # Merge all files content
        for req_file in map(Path, file_deps):
            with req_file.open() as f:
                # Append file content + one empty line
                file_requirements.extend(f.read().splitlines(keepends=False))
                file_requirements.append("")

        # Write merged requirements file
        self.build_from_template(Path(template), self.main_output, {"fileDeps": file_requirements})


class VenvUpdateBuilder(NmkTaskBuilder):
    def build(self, pip_args: str):
        # Prepare outputs
        venv_folder = self.main_output
        venv_status = self.outputs[1]

        # Call pip and touch output folder
        run_pip(
            ["install"]
            + (["-r"] if self.main_input.suffix == ".txt" else [])
            + [str(self.main_input)]
            + (pip_args.strip().split(" ") if len(pip_args) else []),
            logger=self.logger,
        )
        venv_folder.touch()

        # Dump installed packages
        pkg_list = run_pip(["freeze"], logger=self.logger)
        with venv_status.open("w") as f:
            f.write(pkg_list)
