import glob
import os
from typing import List, Optional

from nwon_baseline.file_helper.file import file_extension_from_path


def file_names_in_directory(path_name: str):
    """
    Returns all file names (not the full path!) in a given directory.

    Directories are filtered out
    """

    return [
        os.path.basename(found_path)
        for found_path in file_paths_in_directory(path_name)
    ]


def file_paths_in_directory(
    path_name: str, filter_extensions: Optional[List[str]] = None
) -> List[str]:
    """
    Returns all file paths in a given directory.

    Directories are filtered out.

    Optionally it is possible to filter for certain file extensions.
    File extensions can be defined with or without a dot in the beginning.
    """

    files_in_directory = [
        found_path
        for found_path in paths_in_directory(path_name)
        if os.path.isfile(found_path)
    ]

    if filter_extensions is None:
        return files_in_directory

    extensions = [
        extension if extension.startswith(".") else f".{extension}"
        for extension in filter_extensions
    ]

    return [
        file
        for file in files_in_directory
        if file_extension_from_path(file) in extensions
    ]


def directory_names_in_directory(path_name: str):
    """
    Returns all directory names (not the full path!) in a given directory.

    Files are filtered out.
    """

    return [
        os.path.basename(found_path)
        for found_path in directory_paths_in_directory(path_name)
    ]


def directory_paths_in_directory(path_name: str):
    """
    Returns all directory paths in a given directory.

    Files are filtered out.
    """

    return [
        found_path
        for found_path in paths_in_directory(path_name)
        if os.path.isdir(found_path)
    ]


def get_latest_file_in_directory(path: str):
    list_of_files = glob.glob(os.path.join(path, "*"))

    if len(list_of_files) > 0:
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    return None


def paths_in_directory(directory: str) -> List[str]:
    return [os.path.join(directory, found_path) for found_path in os.listdir(directory)]
