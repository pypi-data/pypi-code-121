""" Classes and functions that enable stand-alone and subprocess workers.
"""
import sys


def oneoff_subprocess_sharedstorage_worker():
    """Implementation of an entry point for running ane instance of a function.

    """
    assert len(sys.argv)==4
    base_dir = sys.argv[1]
    address_prefix = sys.argv[2]
    address_hash_id = sys.argv[3]