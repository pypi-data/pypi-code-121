"""
Utility functions for working with paths and files.
"""
import os


def ensure_path(path: str):
    """
    Checks if the given path exists, and creates it if it does not.

    :param path:    The path.
    """
    if path != '' and not os.path.exists(path):
        os.mkdir(path)
