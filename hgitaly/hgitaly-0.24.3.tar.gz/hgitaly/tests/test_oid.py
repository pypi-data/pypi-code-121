# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from ..oid import (
    tree_oid,
    blob_oid,
    extract_blob_oid,
    extract_tree_oid,
)


def test_tree_oid():
    chgs_id = "01be23ef" * 5
    path = b"s\xfcb/dir"
    repo = None  # actual value not needed for the time being
    oid = tree_oid(repo, chgs_id, path)
    assert extract_tree_oid(repo, oid) == (chgs_id, path)

    oid = tree_oid(repo, chgs_id, b'')
    assert oid != chgs_id
    assert extract_tree_oid(repo, oid) == (chgs_id, b'')


def test_blob_oid():
    chgs_id = "56de78ad" * 5
    path = b"rang\xe9"
    repo = None  # actual value not needed for the time being
    oid = blob_oid(repo, chgs_id, path)
    assert extract_blob_oid(repo, oid) == (chgs_id, path)


def test_commit_oid():
    chgs_id = "56de78ad" * 5
    repo = None  # actual value not needed for the time being
    assert extract_tree_oid(repo, chgs_id) == (chgs_id, None)
