#!/usr/bin/python3

# Copyright (C) 2020 Miguel Simoes, miguelrsimoes[a]yahoo[.]com
# For conditions of distribution and use, see copyright notice in lnsync.py

"""
Provide a simple Python interface to lnsync online and offline databases.
"""

import os

from lnsync_pkg.glob_matcher import ExcludePattern, IncludePattern
from lnsync_pkg.prefixdbname import pick_db_basename, get_default_dbprefix
from lnsync_pkg.filetree import FileTree
from lnsync_pkg.filehashtree import FileHashTree, Mode

def convert_patterns(exclude_patterns):
    pattern_type = {"e": ExcludePattern, "i": IncludePattern}
    if exclude_patterns:
        exclude_patterns = [(pattern_type[inc_or_exc[0]])(glob) \
                            for (inc_or_exc, glob) in exclude_patterns]
    else:
        exclude_patterns = []
    return exclude_patterns

def lnsync_filetree(topdir, exclude_patterns=None):
    exclude_patterns = convert_patterns(exclude_patterns)
    return FileTree(topdir_path=topdir, exclude_patterns=exclude_patterns)

def lnsync_online_db(dbdir, topdir=None, dbprefix=None, exclude_patterns=None):
    """
    Return hashdb.
    exclude_patterns is a list of (inc_or_exc, glob).
        inc_or_exc includes or excludes depending on the first letter, i or e.
    dbdir is where the hashdb is located.
    topdir is the relative subdirectory, default to "".
    """
    if dbprefix is None:
        dbprefix = get_default_dbprefix()
    exclude_patterns = convert_patterns(exclude_patterns)
    filedb_name = pick_db_basename(dbdir, dbprefix=dbprefix)
    if topdir is None:
        topdir = ""
    topdir = os.path.join(dbdir, topdir)
    dbpath = os.path.join(dbdir, filedb_name)
    hashdb = FileHashTree(mode=Mode.ONLINE, topdir_path=topdir,
                          dbkwargs={"dbpath":dbpath},
                          exclude_patterns=exclude_patterns)
    return hashdb

def lnsync_offline_db(dbpath):
    hashdb = FileHashTree(mode=Mode.OFFLINE,
                          topdir_path=None,
                          dbkwargs={"dbpath":dbpath})
    return hashdb
