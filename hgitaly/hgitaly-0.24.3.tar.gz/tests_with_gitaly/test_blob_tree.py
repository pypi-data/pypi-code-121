# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest
import grpc


from hgitaly.oid import (
    blob_oid,
)
from hgitaly.stream import WRITE_BUFFER_SIZE

from hgitaly.stub.shared_pb2 import (
    PaginationParameter,
)
from hgitaly.stub.blob_pb2 import (
    GetBlobRequest,
    GetBlobsRequest,
)
from hgitaly.stub.commit_pb2 import (
    GetTreeEntriesRequest,
    TreeEntryRequest,
)
from hgitaly.stub.blob_pb2_grpc import BlobServiceStub
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


class TreeBlobFixture:

    def __init__(self, gitaly_comparison):
        self.comparison = gitaly_comparison
        self.hg_repo_wrapper = gitaly_comparison.hg_repo_wrapper
        self.git_repo = gitaly_comparison.git_repo

        self.gitaly_repo = gitaly_comparison.gitaly_repo
        self.commit_stubs = dict(
            git=CommitServiceStub(self.comparison.gitaly_channel),
            hg=CommitServiceStub(self.comparison.hgitaly_channel))
        self.blob_stubs = dict(
            git=BlobServiceStub(self.comparison.gitaly_channel),
            hg=BlobServiceStub(self.comparison.hgitaly_channel))

    def tree_entry(self, vcs, path, revision=b'branch/default',
                   limit=0, max_size=0):
        request = TreeEntryRequest(repository=self.gitaly_repo,
                                   revision=revision,
                                   limit=limit,
                                   max_size=max_size,
                                   path=path)
        resp = self.commit_stubs[vcs].TreeEntry(request)
        return [r for r in resp]

    def assert_compare_tree_entry(self, path, several_responses=False, **kw):
        hg_entries = self.tree_entry('hg', path, **kw)
        git_entries = self.tree_entry('hg', path, **kw)

        for entries in (hg_entries, git_entries):
            for r in entries:
                # oid should be the only difference in comparison
                r.oid = ''

        assert hg_entries == git_entries
        if several_responses:
            assert len(hg_entries) > 1

    def assert_error_compare_tree_entry(self, path, **kw):
        with pytest.raises(grpc.RpcError) as hg_err_info:
            self.tree_entry('hg', path, **kw)
        with pytest.raises(grpc.RpcError) as git_err_info:
            self.tree_entry('git', path, **kw)

        assert hg_err_info.value.code() == git_err_info.value.code()
        assert hg_err_info.value.details() == git_err_info.value.details()

    def get_blob(self, vcs, oid, limit=-1):
        request = GetBlobRequest(repository=self.gitaly_repo,
                                 limit=limit,
                                 oid=oid)

        return [r for r in self.blob_stubs[vcs].GetBlob(request)]

    def get_blobs(self, vcs, rev_paths, limit=-1, **request_kw):
        rev_path_msgs = [
            GetBlobsRequest.RevisionPath(revision=rev, path=path)
            for rev, path in rev_paths
        ]
        request = GetBlobsRequest(repository=self.gitaly_repo,
                                  revision_paths=rev_path_msgs,
                                  limit=limit,
                                  **request_kw)

        return [r for r in self.blob_stubs[vcs].GetBlobs(request)]

    def get_tree_entries_raw(self, vcs, path, revision=b'branch/default',
                             pagination=True,
                             cursor='',
                             limit=10,
                             trees_first=False,
                             recursive=False):
        pagination_params = PaginationParameter(
            page_token=cursor, limit=limit) if pagination else None
        if trees_first:
            sort = GetTreeEntriesRequest.SortBy.TREES_FIRST
        else:
            sort = GetTreeEntriesRequest.SortBy.DEFAULT
        request = GetTreeEntriesRequest(repository=self.gitaly_repo,
                                        revision=revision,
                                        pagination_params=pagination_params,
                                        sort=sort,
                                        recursive=recursive,
                                        path=path)

        return self.commit_stubs[vcs].GetTreeEntries(request)

    def get_tree_entries(self, vcs, path, **kw):
        return [entry
                for chunk in self.get_tree_entries_raw(vcs, path, **kw)
                for entry in chunk.entries]

    def assert_compare_get_tree_entries(self, path, **kw):
        hg_tree_entries = self.get_tree_entries('hg', path, **kw)
        git_tree_entries = self.get_tree_entries('git', path, **kw)

        # TODO itertools
        for entry in (e for elist in (git_tree_entries, hg_tree_entries)
                      for e in elist):
            entry.oid = entry.root_oid = ''

        assert hg_tree_entries == git_tree_entries

    def assert_error_compare_get_tree_entries(self, *a, **kw):
        with pytest.raises(grpc.RpcError) as hg_err_info:
            self.get_tree_entries('hg', *a, **kw)
        with pytest.raises(grpc.RpcError) as git_err_info:
            self.get_tree_entries('git', *a, **kw)
        git_err, hg_err = git_err_info.value, hg_err_info.value
        assert git_err.code() == hg_err.code()
        assert git_err.details() == hg_err.details()


@pytest.fixture
def tree_blob_fixture(gitaly_comparison):
    yield TreeBlobFixture(gitaly_comparison)


def test_compare_tree_entry_request(tree_blob_fixture):
    fixture = tree_blob_fixture

    wrapper = fixture.hg_repo_wrapper
    wrapper.write_commit('foo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    wrapper.commit(rel_paths=['sub/bar', 'sub/ba2'],
                   message="zebar", add_remove=True)

    # precondition for the test: mirror worked
    assert fixture.git_repo.branch_titles() == {b'branch/default': b"zebar"}

    for path in (b'sub', b'sub/bar', b'sub/', b'.', b'do-not-exist'):
        fixture.assert_compare_tree_entry(path)

    # limit and max_size (does not apply to Trees)
    fixture.assert_compare_tree_entry(b'foo', limit=4)
    fixture.assert_error_compare_tree_entry(b'foo', max_size=4)
    fixture.assert_compare_tree_entry(b'sub', max_size=1)

    # unknown revision (not an error)
    fixture.assert_compare_tree_entry(b'sub', revision=b'unknown')

    # chunking for big Blob entry
    wrapper.write_commit('bigfile', message="A big file",
                         content=b"big" + b'ff' * WRITE_BUFFER_SIZE)
    fixture.assert_compare_tree_entry(b'bigfile', several_responses=True)

    # reusing content to test GetTreeEntries
    for path in (b'.', b'sub'):
        for recursive in (False, True):
            fixture.assert_compare_get_tree_entries(path, recursive=recursive)

    # sort parameter
    for recursive in (False, True):
        fixture.assert_compare_get_tree_entries(b'.', recursive=recursive,
                                                trees_first=True)

    # tree first and nested trees
    nested = sub / 'nested'
    nested.mkdir()
    (nested / 'deeper').write_text('deep thoughts')
    wrapper.commit_file('sub/nested/deeper', message='deeper')
    assert fixture.git_repo.branch_titles() == {b'branch/default': b"deeper"}
    fixture.assert_compare_get_tree_entries(b'.', recursive=True,
                                            trees_first=True)


def test_compare_get_tree_entries_pagination(tree_blob_fixture):
    fixture = tree_blob_fixture

    wrapper = fixture.hg_repo_wrapper
    wrapper.write_commit('foo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    rel_paths = []
    # Chunk size with Gitaly is big
    for x in range(2900):
        # max file name length is 255 on most filesystems
        path = sub / ('very-' * 46 + '-long-filename-bar%04d' % x)
        path.write_text(str(x))
        rel_paths.append(path)
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    wrapper.commit(rel_paths=rel_paths,
                   message="zebar", add_remove=True)

    def assert_compare_entries_amount(*resp_collections):
        distinct_amounts = set(sum(len(resp.entries) for resp in resps)
                               for resps in resp_collections)
        assert len(distinct_amounts) == 1
        return next(iter(distinct_amounts))

    # asking more than the expected Gitaly first chunk size (2888 entries)
    # but still less than the total
    git_resps, hg_resps = [
        list(fixture.get_tree_entries_raw(vcs, b'sub',
                                          recursive=True,
                                          limit=2890))
        for vcs in ('git', 'hg')
    ]

    # the page token (aka cursor) being an oid, comparison can only be
    # indirect. Chunk sizes are different between Gitaly and HGitaly
    assert len(git_resps) > 1
    assert len(hg_resps) > 1

    assert_compare_entries_amount(git_resps, hg_resps)

    git_cursor, hg_cursor = [resps[0].pagination_cursor.next_cursor
                             for resps in (git_resps, hg_resps)]
    assert git_cursor
    assert hg_cursor

    # cursor is only on first responses (that's probably suboptimal, hence
    # prone to change)
    assert not any(resp.HasField('pagination_cursor')
                   for resps in (git_resps, hg_resps)
                   for resp in resps[1:])

    # using the cursor
    git_resps, hg_resps = [
        list(fixture.get_tree_entries_raw(vcs, b'sub',
                                          recursive=True,
                                          cursor=cursor,
                                          limit=9000))
        for vcs, cursor in (('git', git_cursor),
                            ('hg', hg_cursor))
    ]
    assert_compare_entries_amount(git_resps, hg_resps)

    # negative limit means all results, and there's no cursor if no next page
    git_resps, hg_resps = [
        list(fixture.get_tree_entries_raw(vcs, b'sub',
                                          recursive=True,
                                          limit=-1))
        for vcs in ('git', 'hg')
    ]
    assert_compare_entries_amount(git_resps, hg_resps)
    assert git_resps[0].pagination_cursor == hg_resps[0].pagination_cursor

    # case of limit=0
    git_resps, hg_resps = [
        list(fixture.get_tree_entries_raw(vcs, b'sub',
                                          recursive=True,
                                          limit=0))
        for vcs in ('git', 'hg')
    ]
    assert git_resps == hg_resps  # both are empty

    # case of no params
    git_resps, hg_resps = [
        list(fixture.get_tree_entries_raw(vcs, b'sub',
                                          recursive=True,
                                          pagination=False,
                                          limit=0))
        for vcs in ('git', 'hg')
    ]
    assert_compare_entries_amount(git_resps, hg_resps)

    # case of a cursor that doesn't match any entry (can happen if content
    # changes between requests)

    fixture.assert_error_compare_get_tree_entries(b'sub',
                                                  recursive=True,
                                                  cursor="surely not an OID",
                                                  limit=10)


def test_compare_get_blob_request(tree_blob_fixture):
    fixture = tree_blob_fixture
    git_repo = fixture.git_repo

    wrapper = fixture.hg_repo_wrapper
    large_data = b'\xbe' * WRITE_BUFFER_SIZE + b'\xefdata'

    wrapper.commit_file('small', message="Small file")
    changeset = wrapper.commit_file('foo', message="Large foo",
                                    content=large_data)

    # mirror worked
    assert git_repo.branch_titles() == {b'branch/default': b"Large foo"}

    oids = dict(
        git=fixture.tree_entry('git', b'foo', limit=1)[0].oid,
        hg=blob_oid(wrapper.repo, changeset.hex().decode(), b'foo')
    )

    git_resps = fixture.get_blob('git', oids['git'], limit=12)
    # important assumption for hg implementation:
    assert git_resps[0].oid == oids['git']

    hg_resps = fixture.get_blob('hg', oids['hg'], limit=12)
    assert len(hg_resps) == 1  # double-check: already done in direct hg test
    assert len(git_resps) == 1
    git_resp, hg_resp = git_resps[0], hg_resps[0]
    assert hg_resp.size == git_resp.size
    assert hg_resp.data == git_resp.data

    git_resps = fixture.get_blob('git', oids['git'])

    hg_resps = fixture.get_blob('hg', oids['hg'])
    # Gitaly chunking is not fully deterministic, so the most
    # we can check is that chunking occurs for both servers
    # and that the first and second responses have the same metadata
    assert len(hg_resps) > 1
    assert len(git_resps) > 1

    assert hg_resps[0].oid == oids['hg']
    assert git_resps[0].oid == oids['git']
    assert hg_resps[1].oid == git_resps[1].oid
    for hgr, gitr in zip(hg_resps[:2], git_resps[:2]):
        assert hgr.size == gitr.size

    assert (
        b''.join(r.data for r in hg_resps)
        ==
        b''.join(r.data for r in git_resps)
    )

    # now with get_blobs
    rev_paths = ((b'branch/default', b'small'),
                 (b'branch/default', b'does-not-exist'),
                 (b'no-such-revision', b'small'),
                 )

    hg_resps = fixture.get_blobs('hg', rev_paths)
    git_resps = fixture.get_blobs('git', rev_paths)

    for resp in hg_resps:
        resp.oid = ''
    for resp in git_resps:
        resp.oid = ''

    assert hg_resps == git_resps

    # with limits (the limit is per file)
    hg_resps = fixture.get_blobs('hg', rev_paths, limit=3)
    git_resps = fixture.get_blobs('git', rev_paths, limit=3)

    for resp in hg_resps:
        resp.oid = ''
    for resp in git_resps:
        resp.oid = ''

    assert hg_resps == git_resps

    # chunking in get_blobs, again non-deterministic for Gitaly
    rev_paths = ((b'branch/default', b'small'),
                 (b'branch/default', b'foo'),
                 )
    hg_resps = fixture.get_blobs('hg', rev_paths)
    git_resps = fixture.get_blobs('git', rev_paths)
    assert len(hg_resps) > 2
    assert len(git_resps) > 2
    assert hg_resps[0].oid != ""
    assert git_resps[0].oid != ""
    assert hg_resps[1].oid != ""
    assert git_resps[1].oid != ""
    assert hg_resps[2].oid == ""
    assert git_resps[2].oid == ""
    for hgr, gitr in zip(hg_resps[:3], git_resps[:3]):
        assert hgr.size == gitr.size

    assert (  # content of the big file at 'foo'
        b''.join(r.data for r in hg_resps[1:])
        ==
        b''.join(r.data for r in git_resps[1:])
    )
