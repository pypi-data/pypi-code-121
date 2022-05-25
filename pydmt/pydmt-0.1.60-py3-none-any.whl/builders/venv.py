"""
This module build python virtual envrionments
"""


import os
import shutil

from pydmt.utils.filesystem import mkdir_touch
from pydmt.utils.subprocess import check_call
from pydmt.utils.python import collect_reqs, collect_bootstrap_reqs, get_install_args

from pydmt.api.one_source_one_target import OneSourceOneTarget

SOURCE_FILE = "config/python.py"
TARGET_FOLDER = ".venv/default"


class BuilderVenv(OneSourceOneTarget):
    """
    This is a review of how to build a python virtual environment:
    # create the virtualenv
    virtualenv [folder]
    # activate it
    source [folder]/bin/activate
    # install package
    pip install -r requirements.txt
    """
    def build(self) -> None:
        # remove previous virtual env
        if os.path.isdir(TARGET_FOLDER):
            shutil.rmtree(TARGET_FOLDER)
        # create new virtual env
        args = [
            "virtualenv",
            TARGET_FOLDER,
        ]
        check_call(args)
        # now create bootstrap packages so that we could read config/*.py
        args = [
            "venv-run",
            "--venv",
            ".venv/default",
            "--",
        ]
        args.extend(get_install_args())
        packs = collect_bootstrap_reqs()
        if packs:
            args.extend(packs)
            check_call(args)
        # now install regular packages (we only run the install if there are packages to install)
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
        mkdir_touch(self.target)
