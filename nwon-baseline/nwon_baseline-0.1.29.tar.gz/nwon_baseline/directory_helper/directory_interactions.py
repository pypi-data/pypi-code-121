import os
import shutil
from os import path
from pathlib import Path
from typing import List

from nwon_baseline.directory_helper.directory_content import (
    directory_names_in_directory,
    directory_paths_in_directory,
    file_names_in_directory,
    file_paths_in_directory,
)


def create_pathes(pathes: List[str]) -> None:
    for path_to_create in pathes:
        Path(path_to_create).mkdir(parents=True, exist_ok=True)


def copy_directory(source_directory: str, target_directory: str) -> None:
    if path.exists(target_directory):
        shutil.rmtree(target_directory)

    shutil.copytree(source_directory, target_directory)


def clean_directory(directory: str, recursive: bool = False):
    """
    Cleans all files in a directory. Optionally also deletes all sub
    directories including the containing files
    """

    for file_to_remove in file_paths_in_directory(directory):
        os.remove(file_to_remove)

    if recursive:
        for directory in directory_paths_in_directory(directory):
            shutil.rmtree(directory)
