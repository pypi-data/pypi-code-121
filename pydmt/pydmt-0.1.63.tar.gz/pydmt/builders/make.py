"""
This module runs make
"""


from pydmt.utils.filesystem import mkdir_touch
from pydmt.utils.subprocess import check_call

from pydmt.api.one_source_one_target import OneSourceOneTarget

SOURCE_FILE = "Makefile"
TARGET_FOLDER = ".venv/default"


class BuilderMake(OneSourceOneTarget):
    def build(self) -> None:
        args = [
            "venv-run",
            "--venv",
            ".venv/default",
            "--",
            "make",
        ]
        check_call(args)
        mkdir_touch(self.target)
