# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Git specific things, mostly constants."""

ZERO_SHA_1 = '0' * 40

NULL_COMMIT_ID = ZERO_SHA_1
NULL_BLOB_OID = ZERO_SHA_1

# from `sha1-file.c` in Git 2.28 sources
# we're not dealing for now with the fact that there will be
# two kinds of OIDs with SHA-1 and SHA-256 soon.

# The Git tree object hash that corresponds to an empty tree (directory)
EMPTY_TREE_OID = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

# The Git blob object hash that corresponds to an empty blob (file)
EMPTY_BLOB_OID = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'

OBJECT_MODE_LINK = 0o120000  # symlink to file or directory
OBJECT_MODE_EXECUTABLE = 0o100755  # for blobs only
OBJECT_MODE_NON_EXECUTABLE = 0o100644  # for blobs only
OBJECT_MODE_TREE = 0o40000
