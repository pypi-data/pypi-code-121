import gzip
import os
from typing import Callable, TypeVar, Iterator

# Generic type parameter
T = TypeVar("T")


def get_open_func(filename):
    """
    Gets the open function to use to open the given filename.

    :param filename:    The file to open.
    :return:            The open function, and the read-mode flag to use.
    """

    # Select the open function based on the filename
    if filename.endswith('.gz'):
        return gzip.open, 'rt'
    else:
        return open, 'r'


def load_dir(load_function: Callable[[str], T],
             path: str,
             filename_predicate: Callable[[str], bool],
             recurse: bool = False) -> Iterator[T]:
    """
    Loads all files from the given path that match the filename predicate,
    using the given loading function.

    :param load_function:       The loading function to use to load the files.
    :param path:                The path to the directory to load from.
    :param filename_predicate:  A function which returns True if the file should be loaded,
                                and False if it should not be.
    :param recurse:           Whether sub-directories should be loaded as well.
    :return:                    An iterator over the loaded files.
    """
    # Make sure a valid path was provided
    if not os.path.isdir(path):
        raise ValueError("'" + path + "' is not a directory")

    # Loop through all files/directories in the given directory
    for name in os.listdir(path):
        # Get the full name
        full_name: str = os.path.join(path, name)

        # If we are recursing through directories, do that
        if os.path.isdir(full_name) and recurse:
            for loaded in load_dir(load_function, full_name, filename_predicate, recurse):
                yield loaded

        # Otherwise load the file if the name matches the predicate
        elif os.path.isfile(full_name) and filename_predicate(full_name):
            yield load_function(full_name)
