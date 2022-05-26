# -*- coding: utf-8 -*-
"""The setup script."""
import os
from typing import Iterable, Union, List

from setuptools import setup
from shutil import copytree, rmtree

# Copy the tutorials in cosapp, so they are included in the wheel
def to_ignore(
    folder: Union[bytes, str], filenames: List[Union[bytes, str]]
) -> Iterable[Union[bytes, str]]:
    ignored_files = list()
    for name in filenames:
        if name in (".ipynb_checkpoints",):  # List of subfolders to ignore
            ignored_files.append(name)

        root, ext = os.path.splitext(name)
        if ext not in (
            "",
            ".ipynb",
            ".py",
            ".svg",
        ):  # List of extension to keep - empty ext == subfolder
            ignored_files.append(name)

    return ignored_files


if os.path.exists("cosapp/tutorials"):
    rmtree("cosapp/tutorials")
copytree("docs/tutorials", "cosapp/tutorials", ignore=to_ignore)

# See setup.cfg for all options and MANIFEST.in for data files
setup()

if os.path.exists("cosapp/tutorials"):
    rmtree("cosapp/tutorials")
