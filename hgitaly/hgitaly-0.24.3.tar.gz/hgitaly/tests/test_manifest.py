# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from mercurial_testhelpers import (
    as_bytes,
    RepoWrapper,
)
from .. import manifest


@pytest.fixture
def repo_wrapper(tmpdir):
    yield RepoWrapper.init(tmpdir / 'repo')


def test_directory_listings_integration(repo_wrapper):
    wrapper = repo_wrapper
    base_ctx = wrapper.commit_file('foo')

    sub = wrapper.path / 'sub'
    sub.mkdir()
    (sub / 'bar').write('bar content')
    (sub / 'ba2').write('ba2 content')
    deeper = sub / 'deeper'
    deeper.mkdir()
    (deeper / 'ping').write('pong')

    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2', 'sub/deeper/ping'],
                          message="zebar", add_remove=True)

    assert manifest.miner(base_ctx).ls_dir(b'') == ([], [b'foo'])
    # perhaps we'll want an exception there
    assert manifest.miner(base_ctx).ls_dir(b'sub') == ([], [])

    miner1 = manifest.miner(ctx1)
    assert miner1.ls_dir(b'') == ([b'sub'], [b'foo'])
    assert miner1.ls_dir(b'sub') == ([b'sub/deeper'], [b'sub/ba2', b'sub/bar'])
    assert miner1.ls_dir(b'sub/deeper') == ([], [b'sub/deeper/ping'])

    assert list(miner1.iter_dir_recursive(b'')) == [
        (b'foo', False),
        (b'sub', True),
        (b'sub/ba2', False),
        (b'sub/bar', False),
        (b'sub/deeper', True),
        (b'sub/deeper/ping', False)
    ]


def test_iter_dir_with_flat_paths_integration(repo_wrapper):
    wrapper = repo_wrapper
    wrapper.commit_file('foo')

    sub = wrapper.path / 'sub'
    sub.mkdir()
    (sub / 'bar').write('bar content')
    (sub / 'ba2').write('ba2 content')
    deeper = sub / 'deeper'
    deeper.mkdir()
    (deeper / 'ping').write('pong')

    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2', 'sub/deeper/ping'],
                          message="zebar", add_remove=True)

    miner1 = manifest.miner(ctx1)
    assert list(miner1.iter_dir_with_flat_paths(b'')) == [
        (b'foo', False, b'foo'),
        (b'sub', True, b'sub'),
    ]
    assert list(miner1.iter_dir_with_flat_paths(b'sub')) == [
        (b'sub/ba2', False, b'sub/ba2'),
        (b'sub/bar', False, b'sub/bar'),
        (b'sub/deeper', True, b'sub/deeper'),
    ]


class FakeChangeset:
    """Simply encapsulating a list of file paths.

    The goal is to have `self.manifest.iterkeys()` iterate over the
    given file paths.
    """
    def __init__(self, file_paths):
        self.file_paths = [as_bytes(fp) for fp in file_paths]

    def manifest(self):
        return self

    def iterkeys(self):
        return iter(self.file_paths)


def ls_with_flat_paths(path, file_paths):
    """Call iter_dir_with_flat_path for path on a FakeChangeset
    """
    miner = manifest.miner(FakeChangeset(file_paths))
    return list(miner.iter_dir_with_flat_paths(as_bytes(path)))


def reference_ls_flat_paths(top_path, manifest_paths):
    """Reproduction in Python of the reference lang implementation.

    It uses `ManifestMiner.ls_dir()`, which of course would be a
    very inefficient implementation.
    """
    top_path = as_bytes(top_path)
    miner = manifest.miner(FakeChangeset(manifest_paths))

    def ls_dir(path):
        subdirs, filepaths = miner.ls_dir(path)
        entries = [(p, True) for p in subdirs]
        entries.extend((p, False) for p in filepaths)
        entries.sort()
        return entries

    entries = ls_dir(top_path)
    res = []
    # starts to being compared to Gitaly's populateFlatPath here
    # differences:
    # - our entries are just tuples (path, is_dir)
    # - we output a list of (path, is_dir, flat_path)
    # - we don't need a maximum recursion constant in these tests
    for path, is_dir in entries:
        flat_path = path

        if not is_dir:
            res.append((path, is_dir, flat_path))
            continue

        while True:
            sub_entries = ls_dir(flat_path)
            if len(sub_entries) != 1 or not sub_entries[0][1]:
                break
            subentry_dirs, subentry_files = miner.ls_dir(flat_path)
            flat_path = subentry_dirs[0]

        res.append((path, is_dir, flat_path))
    return res


def test_iter_dir_recursive():
    # deeply nested case: no duplicates and in direct traversal order
    miner = manifest.miner(FakeChangeset(('a', 'b/c/d/e', 'b/c/d/f', 'out')))
    assert list(miner.iter_dir_recursive(b'b')) == [
        (b'b/c', True),
        (b'b/c/d', True),
        (b'b/c/d/e', False),
        (b'b/c/d/f', False),
    ]
    assert list(miner.iter_dir_recursive(b'')) == [
        (b'a', False),
        (b'b', True),
        (b'b/c', True),
        (b'b/c/d', True),
        (b'b/c/d/e', False),
        (b'b/c/d/f', False),
        (b'out', False),
    ]


def test_iter_dir_with_flat_path():
    for path, manifest_paths in [
            ('a', ['a/b']),
            ('', ['a/b']),
            ('', ['a/b', 'a/c']),
            ('a', ['a/b/c', 'd']),
            ('a', ['a/b/c', 'a/b/d', 'a/e']),
            ('a', ['a/b/c/d/x', 'a/b/c/d/y', 'a/e']),
            ('a', ['a/b/c/d/x', 'a/b/c/d/y', 'a/b/x']),
            ('a', ['a/b/c', 'a/b/d', 'a/e']),
            ('a', ['a/b/c/d/x', 'a/b/c/d/y', 'a/e']),
            ('a', ['a/b/c/d/x', 'a/b/c/d/y', 'a/b/x']),
    ]:
        actual = ls_with_flat_paths(path, manifest_paths)
        expected = reference_ls_flat_paths(path, manifest_paths)
        assert actual == expected
