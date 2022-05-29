"""
This module build python virtual envrionments
"""


import os
import shutil
from typing import List, Generator, Tuple

from pydmt.api.builder import Builder, Node, SourceFile, TargetFolder
from pydmt.utils.filesystem import files_under_folder
from pydmt.utils.digest import sha1_file
from pydmt.utils.subprocess import check_call
from pydmt.utils.python import collect_reqs, get_install_args

SOURCE_FILE = "config/python.py"
TARGET_FOLDER = ".venv/default"


class BuilderVenvFull(Builder):
    """
    This is a review of how to build a python virtual environment:
    # create the virtualenv
    virtualenv [folder]
    # activate it
    source [folder]/bin/activate
    # install package
    pip install -r requirements.txt
    """
    def __init__(self):
        # pylint: disable=useless-super-delegation
        super().__init__()

    def get_sources(self) -> List[Node]:
        file_list = [SourceFile(SOURCE_FILE)]
        return file_list

    def get_targets(self) -> List[Node]:
        return [TargetFolder(TARGET_FOLDER)]

    def build(self) -> None:
        if os.path.isdir(TARGET_FOLDER):
            shutil.rmtree(TARGET_FOLDER)
        args = [
            "virtualenv",
            TARGET_FOLDER,
        ]
        check_call(args)
        args = [
            "venv-run",
            "--venv",
            ".venv/default",
            "--",
        ]
        args.extend(get_install_args())
        packs = collect_reqs()
        if packs:
            args.extend(packs)
            check_call(args)

    def yield_results(self) -> Generator[Tuple[str, str], None, None]:
        for x in files_under_folder(TARGET_FOLDER):
            yield sha1_file(x), x
