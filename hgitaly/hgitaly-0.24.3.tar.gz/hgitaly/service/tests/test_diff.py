# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
from mercurial.pycompat import sysstr
import pytest
from hgitaly.git import (
    EMPTY_TREE_OID,
)
from hgitaly.tests.common import (
    make_empty_repo,
)
from hgitaly.stub.diff_pb2 import (
    CommitDeltaRequest,
    CommitDiffRequest,
    ChangedPaths,
    DiffStatsRequest,
    RawDiffRequest,
    RawPatchRequest,
    FindChangedPathsRequest,
)
from mercurial import (
    node,
)
from hgitaly.stub.diff_pb2_grpc import DiffServiceStub


def test_raw_diff(grpc_channel, server_repos_root):
    grpc_stub = DiffServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx0 = wrapper.commit_file('foo', content="I am oof\n",
                               message=b'added foo')
    ctx1 = wrapper.commit_file('foo', content="I am foo\n",
                               message=b'changes foo')
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    wrapper.command(b'ci', message=b"rename foo to zoo")
    ctx2 = wrapper.repo[b'.']
    sha0, sha1, sha2 = ctx0.hex(), ctx1.hex(), ctx2.hex()

    def do_rpc(left_sha, right_sha):
        request = RawDiffRequest(
                    repository=grpc_repo,
                    left_commit_id=left_sha,
                    right_commit_id=right_sha,
                  )
        response = grpc_stub.RawDiff(request)
        return b''.join(resp.data for resp in response)

    # case 1: actual test
    resp = do_rpc(sha0, sha1)
    respheader = (
        b'diff --git a/foo b/foo\n'
    )
    resphunk = (
        b'--- a/foo\n'
        b'+++ b/foo\n'
        b'@@ -1,1 +1,1 @@\n'
        b'-I am oof\n'
        b'+I am foo\n'
    )
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 2: with null node
    resp = do_rpc(node.nullhex, sha0)
    respheader = (
        b'diff --git a/foo b/foo\n'
    )
    resphunk = (
        b'--- /dev/null\n'
        b'+++ b/foo\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am oof\n'
    )
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 2bis: with null left node, expressed as empty tree
    # this is really used by the Rails app.
    resp = do_rpc(EMPTY_TREE_OID, sha0)
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 2ter: with null right node, expressed as empty tree
    # this is for completeness
    resp = do_rpc(sha0, EMPTY_TREE_OID)
    resphunk = (
        b'--- a/foo\n'
        b'+++ /dev/null\n'
        b'@@ -1,1 +0,0 @@\n'
        b'-I am oof\n'
    )
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 3: with file renaming
    resp = do_rpc(sha1, sha2)
    assert resp == (
        b'diff --git a/foo b/zoo\n'
        b'similarity index 100%\n'
        b'rename from foo\n'
        b'rename to zoo\n'
    )

    # case 4: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    # varient 1
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha0, sha_not_exists)
    assert exc_info.value.code() == grpc.StatusCode.UNKNOWN
    assert 'exit status 128' in exc_info.value.details()
    # varient 2
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha_not_exists, sha0)
    assert exc_info.value.code() == grpc.StatusCode.UNKNOWN
    assert 'exit status 128' in exc_info.value.details()


def test_raw_patch(grpc_channel, server_repos_root):
    grpc_stub = DiffServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # prepare repo as:
    #
    #   @    3 merge with stable
    #   |\
    #   | o  2 added bar (branch: stable)
    #   | |
    #   o |  1 changes foo (topic: feature)
    #   |/
    #   o  0 added foo
    #
    #
    dayoffset = 86400  # seconds in 24 hours
    ctx0 = wrapper.commit_file('foo', content="I am oof\n",
                               message=b'added foo', user=b'testuser',
                               utc_timestamp=dayoffset)
    ctx1 = wrapper.commit_file('foo', content="I am foo\n", topic=b'feature',
                               message=b'changes foo', user=b'testuser',
                               utc_timestamp=dayoffset*2)
    ctx2 = wrapper.commit_file('bar', content="I am bar\n",
                               message=b'added bar', user=b'testuser',
                               utc_timestamp=dayoffset*3, parent=ctx0,
                               branch=b'stable')
    wrapper.update(ctx1.rev())
    ctx3 = wrapper.merge_commit(ctx2, user=b'testuser',
                                utc_timestamp=dayoffset*4,
                                message=b'merge with stable')
    sha0, sha2, sha3 = ctx0.hex(), ctx2.hex(), ctx3.hex()

    def do_rpc(left_sha, right_sha):
        request = RawPatchRequest(
                    repository=grpc_repo,
                    left_commit_id=left_sha,
                    right_commit_id=right_sha,
                  )
        response = grpc_stub.RawPatch(request)
        return b''.join(resp.data for resp in response)

    # with null revision
    null_node = b"00000" * 5
    assert do_rpc(null_node, sha0) == (
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 86400 0\n'
        b'#      Fri Jan 02 00:00:00 1970 +0000\n'
        b'# Node ID f1a2b5b072f5e59abd43ed6982ab428a6149eda8\n'
        b'# Parent  0000000000000000000000000000000000000000\n'
        b'added foo\n'
        b'\n'
        b'diff --git a/foo b/foo\n'
        b'new file mode 100644\n'
        b'--- /dev/null\n'
        b'+++ b/foo\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am oof\n'
    )
    # with merge commit
    assert do_rpc(sha2, sha3) == (
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 172800 0\n'
        b'#      Sat Jan 03 00:00:00 1970 +0000\n'
        b'# Node ID 0ae85a0d494d9197fd2bf8347d7fff997576f25a\n'
        b'# Parent  f1a2b5b072f5e59abd43ed6982ab428a6149eda8\n'
        b'# EXP-Topic feature\n'
        b'changes foo\n'
        b'\n'
        b'diff --git a/foo b/foo\n'
        b'--- a/foo\n'
        b'+++ b/foo\n'
        b'@@ -1,1 +1,1 @@\n'
        b'-I am oof\n'
        b'+I am foo\n'
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 345600 0\n'
        b'#      Mon Jan 05 00:00:00 1970 +0000\n'
        b'# Node ID 2215a964a3245ee4e7c3906f076b14977152a1df\n'
        b'# Parent  0ae85a0d494d9197fd2bf8347d7fff997576f25a\n'
        b'# Parent  c4fa3ef1fc8ba157ed8c26584c13492583bf17e9\n'
        b'# EXP-Topic feature\n'
        b'merge with stable\n'
        b'\n'
        b'diff --git a/bar b/bar\n'
        b'new file mode 100644\n'
        b'--- /dev/null\n'
        b'+++ b/bar\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am bar\n'
    )
    # with different branch
    assert do_rpc(sha0, sha2) == (
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 259200 0\n'
        b'#      Sun Jan 04 00:00:00 1970 +0000\n'
        b'# Branch stable\n'
        b'# Node ID c4fa3ef1fc8ba157ed8c26584c13492583bf17e9\n'
        b'# Parent  f1a2b5b072f5e59abd43ed6982ab428a6149eda8\n'
        b'added bar\n'
        b'\n'
        b'diff --git a/bar b/bar\n'
        b'new file mode 100644\n'
        b'--- /dev/null\n'
        b'+++ b/bar\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am bar\n'
    )
    # when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    # varient 1
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha0, sha_not_exists)
    assert exc_info.value.code() == grpc.StatusCode.UNKNOWN
    assert 'exit status 128' in exc_info.value.details()
    # varient 2
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha_not_exists, sha0)
    assert exc_info.value.code() == grpc.StatusCode.UNKNOWN
    assert 'exit status 128' in exc_info.value.details()


def test_commit_diff(grpc_channel, server_repos_root):
    grpc_stub = DiffServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Add bar")
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    ctx2 = wrapper.commit([b'bar', b'zar'], message="Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    # Repo structure:
    #
    # @  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    def do_rpc(left_cid, right_cid, **kwargs):
        hgitaly_request = CommitDiffRequest(
                            repository=grpc_repo,
                            left_commit_id=left_cid,
                            right_commit_id=right_cid, **kwargs
                        )
        response = grpc_stub.CommitDiff(hgitaly_request)
        return [resp for resp in response]

    # case 1: when a file renamed
    resp = do_rpc(left_cid=ctx1.hex(), right_cid=ctx2.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'bar'
    assert resp.to_path == b'zar'
    assert resp.raw_patch_data == b''
    assert resp.old_mode == resp.new_mode

    # case 2: when a new file added
    resp = do_rpc(left_cid=ctx2.hex(), right_cid=ctx3.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.raw_patch_data == b'@@ -0,0 +1,2 @@\n+I am in\n+zoo\n'
    assert resp.old_mode == 0
    assert resp.new_mode == 0o100644

    # case 3: test with enforce_limits
    # Note: For thorough testing, look at comparison tests
    resp = do_rpc(
        left_cid=ctx2.hex(),
        right_cid=ctx3.hex(),
        enforce_limits=True,
        max_files=10,
        max_bytes=100,
        max_lines=1,
    )
    assert len(resp) == 1
    assert resp[0].overflow_marker

    # case 4: test with collapse_diffs
    # Note: For thorough testing, look at comparison tests
    resp = do_rpc(
        left_cid=ctx2.hex(),
        right_cid=ctx3.hex(),
        collapse_diffs=True,
        safe_max_files=10,
        safe_max_bytes=100,
        safe_max_lines=1,
    )
    assert len(resp) == 1
    assert resp[0].collapsed

    # case 5: test with paths
    resp = do_rpc(left_cid=ctx0.hex(), right_cid=ctx3.hex(), paths=[b'zoo'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.from_path == b'zoo'
    assert resp.raw_patch_data == b'@@ -0,0 +1,2 @@\n+I am in\n+zoo\n'

    # case 6: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha_not_exists, ctx3.hex())
    assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE


def test_commit_delta(grpc_channel, server_repos_root):
    grpc_stub = DiffServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Add bar")
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    ctx2 = wrapper.commit([b'bar', b'zar'], message="Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    # Repo structure:
    #
    # @  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    def do_rpc(left_cid, right_cid, **kwargs):
        hgitaly_request = CommitDeltaRequest(
                            repository=grpc_repo,
                            left_commit_id=left_cid,
                            right_commit_id=right_cid, **kwargs
                        )
        response = grpc_stub.CommitDelta(hgitaly_request)
        deltas = []
        for resp in response:
            deltas.append(*resp.deltas)
        return deltas

    # case 1: when a file renamed
    resp = do_rpc(left_cid=ctx1.hex(), right_cid=ctx2.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'bar'
    assert resp.to_path == b'zar'
    assert resp.old_mode == resp.new_mode

    # case 2: when a new file added
    resp = do_rpc(left_cid=ctx2.hex(), right_cid=ctx3.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.old_mode == 0
    assert resp.new_mode == 0o100644

    # case 3: test with paths
    resp = do_rpc(left_cid=ctx0.hex(), right_cid=ctx3.hex(), paths=[b'zoo'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.from_path == b'zoo'

    # case 3.a
    resp = do_rpc(left_cid=ctx1.hex(), right_cid=ctx2.hex(), paths=[b'zar'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'zar'
    assert resp.to_path == b'zar'
    assert resp.old_mode == 0
    assert resp.new_mode == 0o100644

    # case 3.b
    resp = do_rpc(left_cid=ctx1.hex(), right_cid=ctx2.hex(), paths=[b'bar'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'bar'
    assert resp.to_path == b'bar'
    assert resp.old_mode == 0o100644
    assert resp.new_mode == 0

    # case 4: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha_not_exists, ctx3.hex())
    assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE


def test_diff_stats(grpc_channel, server_repos_root):
    grpc_stub = DiffServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    wrapper.commit_file('bar', content="I am in\nrab\n",
                        message="Add bar")
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    ctx2 = wrapper.commit([b'bar', b'zar'], message="Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    # Repo structure:
    #
    # @  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    def do_rpc(left_cid, right_cid):
        hgitaly_request = DiffStatsRequest(
                            repository=grpc_repo,
                            left_commit_id=left_cid,
                            right_commit_id=right_cid
                        )
        response = grpc_stub.DiffStats(hgitaly_request)
        res = []
        for resp in response:
            res.append(*resp.stats)
        return res

    # case 1: when a file renamed
    resp = do_rpc(left_cid=ctx1.hex(), right_cid=ctx2.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.old_path == b'bar'
    assert resp.path == b'zar'
    assert not resp.additions
    assert not resp.deletions

    # case 2: when a new file added
    resp = do_rpc(left_cid=ctx2.hex(), right_cid=ctx3.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert not resp.old_path
    assert resp.path == b'zoo'
    assert resp.additions == 2
    assert not resp.deletions

    # case 3: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha_not_exists, ctx3.hex())
    assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE


def test_find_changed_paths(grpc_channel, server_repos_root):
    grpc_stub = DiffServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    (wrapper.path / 'foo').write_text('foo content')
    (wrapper.path / 'bar').write_text('bar content')
    (wrapper.path / 'zoo').write_text('zoo content')
    wrapper.commit(rel_paths=['foo', 'bar', 'zoo'],
                   add_remove=True)
    (wrapper.path / 'too').write_text('too content')
    (wrapper.path / 'foo').write_text('foo content modified')
    (wrapper.path / 'bar').unlink()
    wrapper.command(b'cp', wrapper.repo.root + b'/zoo',
                    wrapper.repo.root + b'/zaz')
    ctx1 = wrapper.commit(rel_paths=['foo', 'bar', 'zaz', 'too'],
                          add_remove=True)

    def do_rpc(commits):
        request = FindChangedPathsRequest(
            repository=grpc_repo,
            commits=commits,
        )
        response = grpc_stub.FindChangedPaths(request)
        resp_dict = dict()
        for resp in response:
            for changed_path in resp.paths:
                resp_dict[changed_path.path] = changed_path.status
        return resp_dict

    # Actual test (for ctx1)
    resp_dict = {
        b'too': ChangedPaths.Status.ADDED,
        b'foo': ChangedPaths.Status.MODIFIED,
        b'bar': ChangedPaths.Status.DELETED,
        b'zaz': ChangedPaths.Status.COPIED,
    }
    assert do_rpc([ctx1.hex()]) == resp_dict

    # when commit_id does not correspond to a commit
    wrong_cid = b'12face12' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc([wrong_cid])
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    assert (
        'FindChangedPaths: commit: %s can not be found' % (sysstr(wrong_cid))
        ==
        exc_info.value.details()
    )
