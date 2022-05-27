"""
Test suite for package functionality
"""
import os


def get_resource(path):
    """
    Get resource in tests/bin/
    """
    dirname = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(dirname, "bin", path))
