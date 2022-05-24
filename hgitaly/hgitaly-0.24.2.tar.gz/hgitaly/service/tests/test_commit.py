# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import pytest
import time
from mercurial import (
    pycompat,
)
from google.protobuf.timestamp_pb2 import Timestamp
from hgext3rd.heptapod.branch import set_default_gitlab_branch

from hgitaly.oid import (
    tree_oid,
    blob_oid,
)

from hgitaly.tests.common import (
    make_empty_repo,
    make_tree_shaped_repo,
)

from hgitaly.stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitsByMessageRequest,
    CommitStatsRequest,
    CountCommitsRequest,
    CountDivergingCommitsRequest,
    FindCommitRequest,
    FindCommitsRequest,
    FindAllCommitsRequest,
    GetCommitMessagesRequest,
    GetTreeEntriesRequest,
    LastCommitForPathRequest,
    ListCommitsByOidRequest,
    ListCommitsByRefNameRequest,
    ListCommitsRequest,
    ListFilesRequest,
    ListLastCommitsForTreeRequest,
    RawBlameRequest,
    TreeEntry,
    TreeEntryRequest,
    TreeEntryResponse,
)
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub

from hgitaly.stub.shared_pb2 import (
    PaginationParameter,
)


def test_is_ancestor(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    _, grpc_repo, changesets = make_tree_shaped_repo(server_repos_root)

    def hex_is_ancestor(hex1, hex2):
        resp = grpc_stub.CommitIsAncestor(
            CommitIsAncestorRequest(repository=grpc_repo,
                                    ancestor_id=hex1,
                                    child_id=hex2,
                                    ))
        return resp.value

    def is_ancestor(key1, key2):
        return hex_is_ancestor(changesets[key1].hex(), changesets[key2].hex())

    assert is_ancestor('base', 'top1')
    assert not is_ancestor('other_base', 'default')
    assert is_ancestor('default', 'default')
    assert is_ancestor('other_base', 'wild2')

    base_hex = changesets['base'].hex()
    # id in message *has* logically to be 40 chars
    # technically, on current Mercurial if short_id is str, repo[short_id]
    # does not work but repo[full_id] does.
    unknown_hex = '1234dead' * 5

    assert hex_is_ancestor(base_hex, unknown_hex) is False
    assert hex_is_ancestor(unknown_hex, base_hex) is False


def test_is_ancestor_obsolete(grpc_channel, server_repos_root):
    # still works if one of the changesets becomes obsolete
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx1 = wrapper.write_commit('foo')
    ctx2 = wrapper.write_commit('foo2')

    wrapper.command('amend', message=b'amended')
    assert grpc_stub.CommitIsAncestor(
        CommitIsAncestorRequest(repository=grpc_repo,
                                ancestor_id=ctx1.hex(),
                                child_id=ctx2.hex(),
                                ))


# TODO test with tags. In particular they have precedence in Mercurial
# over branches
def test_find_commit(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    now = time.time()
    ctx = wrapper.write_commit('foo',
                               utc_timestamp=now,
                               message="A single line",
                               user="HGitaly Test <hgitaly@heptapod.test>")
    ctx2 = wrapper.write_commit('foo',
                                tz_timestamp=(123456, -7200),  # UTC+2
                                parent=ctx,
                                message="Foo deux\n\nA very interesting bar")

    def do_rpc(revision):
        request = FindCommitRequest(repository=grpc_repo, revision=revision)
        return grpc_stub.FindCommit(request)

    commit = do_rpc(ctx.hex()).commit
    assert commit is not None
    assert commit.id == ctx.hex().decode()
    assert commit.parent_ids == []
    assert commit.author.name == b"HGitaly Test"
    assert commit.author.email == b"hgitaly@heptapod.test"
    assert commit.author.date.seconds == int(now)
    assert commit.author.timezone == b'+0000'
    assert commit.subject == b"A single line"
    assert commit.body == commit.subject
    assert commit.body_size == 13

    commit2 = do_rpc(ctx2.hex()).commit
    assert commit2 is not None
    assert commit2.subject == b'Foo deux'
    assert commit2.body == b"Foo deux\n\nA very interesting bar"
    assert commit2.body_size == 32
    assert commit2.parent_ids == [ctx.hex().decode()]
    assert commit2.author.timezone == b'+0200'

    # TODO check with two parents, it'd be nice to have a helper to create
    # merge commits very quickly
    assert do_rpc(b'branch/default').commit == commit2

    # default GitLab branch not being set, there is no fallback
    assert not do_rpc(b'HEAD').HasField('commit')

    top_ctx = wrapper.write_commit('animals',
                                   message="in topic",
                                   topic='antelope',
                                   parent=ctx)
    commit_top = do_rpc(b'topic/default/antelope').commit
    assert commit_top is not None
    assert commit_top.subject == b"in topic"

    # with revision given in full "ref" form
    assert do_rpc(b'refs/heads/topic/default/antelope').commit == commit_top

    # with explicitely set default GitLab branch:
    set_default_gitlab_branch(wrapper.repo, b'topic/default/antelope')
    assert do_rpc(b'HEAD').commit == commit_top

    # with obsolete changeset given by full node id
    wrapper.command('amend', message=b'amended')
    assert do_rpc(top_ctx.hex()).commit == commit_top

    # with unknown changeset
    assert not do_rpc(b'unknown').HasField('commit')


def test_find_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    # set default branch
    set_default_gitlab_branch(wrapper.repo, b'branch/default')
    # prepare repo as:
    #
    #   @    4 (branch/default) merge with stable
    #   |\
    #   | o  3 creates 'animal' (branch/stable)
    #   | |
    #   o |  2 rename 'foo' to 'zoo' (user: testuser2)
    #   |/
    #   | 1 changes 'foo'
    #   |/
    #   o  0  creates 'foo'
    #

    def do_rpc(limit=10, **opts):
        request = FindCommitsRequest(repository=grpc_repo, limit=limit, **opts)
        resp = grpc_stub.FindCommits(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]
    ctx0 = wrapper.write_commit('foo')
    ctx1 = wrapper.write_commit('foo')
    wrapper.update(0)
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    ctx2 = wrapper.commit([b'foo', b'zoo'], message=b"rename foo to zoo")
    # commits with different date/time, to test with date filter later
    timestamp = int(time.time())
    ctx3 = wrapper.write_commit('animals', branch='stable', parent=ctx0,
                                utc_timestamp=timestamp+10, user='testuser2')
    wrapper.update(2)
    ctx4 = wrapper.merge_commit(ctx3, message=b'merge with stable',
                                utc_timestamp=timestamp+20)
    sha0, sha1, sha2, sha3, sha4 = (ctx0.hex(), ctx1.hex(), ctx2.hex(),
                                    ctx3.hex(), ctx4.hex())
    # with follow; test that it follows renames
    assert do_rpc(paths=[b'zoo'], follow=True) == [sha2, sha0]
    # with revision
    assert do_rpc(revision=b'4...1') == [sha4, sha3, sha2, sha1]
    assert do_rpc(revision=b'0..4') == [sha4, sha3, sha2]
    # use default branch if any of the side is omitted
    assert do_rpc(revision=b'...1') == [sha4, sha3, sha2, sha1]
    assert do_rpc(revision=b'1...') == [sha4, sha3, sha2, sha1]
    assert do_rpc(revision=b'0..') == [sha4, sha3, sha2]
    assert do_rpc(revision=b'..0') == []
    # when revision does not exists
    assert do_rpc(revision=b'does_not_exists') == []
    # with all, return all the commits
    assert do_rpc(all=True) == [sha0, sha1, sha2, sha3, sha4]
    # with offset
    assert do_rpc(all=True, offset=2) == [sha2, sha3, sha4]
    # with skip_merges
    assert do_rpc(skip_merges=True) == [sha3, sha2, sha0]

    # with date specs
    date, date2 = Timestamp(), Timestamp()
    date.FromSeconds(timestamp+10)
    assert do_rpc(before=date) == [sha3, sha2, sha0]
    assert do_rpc(after=date) == [sha4, sha3]
    # gracinet: given that before is < and after is > I didn't expect
    # after=before to return anything, but `hg help dates` says that
    # the `to` range specifier is inclusive.
    assert do_rpc(after=date, before=date) == [sha3]
    date2.FromSeconds(timestamp+100)
    assert do_rpc(after=date, before=date2) == [sha4, sha3]

    # with pats, return commits containing changes to pats
    assert do_rpc(paths=[b'foo', b'animals']) == [sha3, sha0]
    # when no revision passed; return revs("reverse(::default_tip)")
    assert do_rpc() == [sha4, sha3, sha2, sha0]
    # with limit
    assert do_rpc(limit=0) == []
    assert do_rpc(limit=2) == [sha4, sha3]
    # with author
    assert do_rpc(all=True, author=b"testuser2") == [sha3]
    # with order
    ctx5 = wrapper.write_commit('foo', parent=ctx1)
    sha5 = ctx5.hex()
    assert do_rpc(all=True, order=FindCommitsRequest.Order.TOPO) == [
        sha0, sha2, sha3, sha4, sha1, sha5]


def test_commits_by_message(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    set_default_gitlab_branch(wrapper.repo, b'branch/default')
    # repo structure:
    #
    #   o 2 add animal (branch/stable)
    #   |
    #   | 1 add bar
    #   |/
    #   o 0 add foo
    #

    def do_rpc(**opts):
        request = CommitsByMessageRequest(repository=grpc_repo, **opts)
        resp = grpc_stub.CommitsByMessage(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]
    ctx0 = wrapper.write_commit('foo', message=b'add foo')
    ctx1 = wrapper.write_commit('bar', parent=ctx0, message=b'add bar')
    ctx2 = wrapper.write_commit('animal', branch='stable', parent=ctx0,
                                message=b'add animal')
    sha0, sha1, sha2 = ctx0.hex(), ctx1.hex(), ctx2.hex()

    # without revision; use default branch set in repo config
    assert do_rpc(query=b'add') == [sha1, sha0]
    assert do_rpc(query=b'bar') == [sha1]
    assert do_rpc(query=b'foo') == [sha0]
    # with revision
    assert do_rpc(revision=b'branch/stable', query=b'add') == [sha2, sha0]
    # when revision does not exists
    assert do_rpc(revision=b'does_not_exists', query=b'add') == []
    # with no arg
    assert do_rpc() == []
    # with offset
    assert do_rpc(query=b'add', offset=1) == [sha0]
    # with limit
    assert do_rpc(query=b'add', limit=1) == [sha1]
    # with path
    assert do_rpc(query=b'add', path=b'foo') == [sha0]


def test_find_all_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    # prepare repo as:
    #
    #   o  3 (branch/stable)
    #   |
    #   | o  2 user: testuser2
    #   |/
    #   | 1 changes 'foo'
    #   |/
    #   o  0  creates 'foo'
    #

    def do_rpc(**opts):
        request = FindAllCommitsRequest(repository=grpc_repo, **opts)
        resp = grpc_stub.FindAllCommits(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]
    ctx0 = wrapper.write_commit('foo')
    timestamp = int(time.time())
    # commits with different date/time, to test with date ordering
    ctx1 = wrapper.write_commit('foo', parent=ctx0, utc_timestamp=timestamp+10)
    ctx2 = wrapper.write_commit('bar', parent=ctx0, user="testuser2",
                                utc_timestamp=timestamp+20)
    ctx3 = wrapper.write_commit('animals', branch='stable', parent=ctx0,
                                utc_timestamp=timestamp+15)
    sha0, sha1, sha2, sha3 = ctx0.hex(), ctx1.hex(), ctx2.hex(), ctx3.hex()

    # with revision
    assert do_rpc(revision=b'branch/stable') == [sha3, sha0]
    assert do_rpc(revision=b'branch/default') == [sha2, sha0]
    # when revision does not exists
    assert do_rpc(revision=b'does_not_exists') == []
    # with no arg, return all the commits
    assert do_rpc() == [sha3, sha2, sha1, sha0]
    # with skip
    assert do_rpc(skip=2) == [sha1, sha0]
    # with max_count
    assert do_rpc(max_count=2) == [sha3, sha2]
    # with date order (note that ctx2 date is latest than ctx3)
    assert do_rpc(order='DATE') == [sha2, sha3, sha1, sha0]
    # with topo order
    assert do_rpc(order='TOPO') == [sha3, sha2, sha1, sha0]
    # with obsolete revision (done at the end for no repercussions)
    wrapper.prune(sha3)
    assert ctx3.obsolete()
    assert do_rpc(revision=sha3) == [sha3, sha0]


def test_list_commits_by_ref_name(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def do_rpc(ref_names):
        request = ListCommitsByRefNameRequest(repository=grpc_repo,
                                              ref_names=ref_names)
        response = grpc_stub.ListCommitsByRefName(request)
        return {ref.ref_name: ref.commit.id.encode('ascii')
                for chunk in response for ref in chunk.commit_refs}

    # prepare repo as:
    #
    #   2 (branch/default)
    #   |
    #   1
    #   |  3 (topic/default/feature)
    #   | /
    #   0
    #
    ctx0 = wrapper.write_commit('foo')
    wrapper.write_commit('bar')
    ctx2 = wrapper.write_commit('baz')
    ctx3 = wrapper.write_commit('animals', topic='feature', parent=ctx0)

    assert do_rpc(
        [b"branch/default", b"topic/default/feature", b"not_exists"]
    ) == {
        b"branch/default": ctx2.hex(),
        b"topic/default/feature": ctx3.hex()
    }


def test_count_diverging_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def do_rpc(gl_from, gl_to, max_count=None):
        request = CountDivergingCommitsRequest(repository=grpc_repo,
                                               to=gl_to,
                                               max_count=max_count)
        setattr(request, 'from', gl_from)
        response = grpc_stub.CountDivergingCommits(request)
        return [response.left_count, response.right_count]

    # prepare repo as:
    #
    #   2 (branch/default)
    #   |
    #   1
    #   |  3 (topic/default/feature)
    #   | /
    #   0
    #
    ctx0 = wrapper.write_commit('foo')
    wrapper.write_commit('bar')
    wrapper.write_commit('baz')
    top_ctx = wrapper.write_commit('animals', topic='feature', parent=ctx0)

    assert do_rpc(b"branch/default", b"topic/default/feature") == [2, 1]
    # with commit given by full id
    assert do_rpc(b"branch/default", top_ctx.hex()) == [2, 1]
    # count 0 for the same "from" and "to"
    assert do_rpc(b"branch/default", b"branch/default") == [0, 0]
    # when one of them is invalid ref
    assert do_rpc(b"branch/default", b"does-not-exists") == [0, 0]
    assert do_rpc(b"does-not-exists", b"branch/default") == [0, 0]
    # count bounded with max_count
    for max_count in [1, 2, 3]:
        resp = do_rpc(b"branch/default", b"topic/default/feature", max_count)
        assert (resp[0] + resp[1]) == max_count
        resp = do_rpc(b"topic/default/feature", b"branch/default", max_count)
        assert (resp[0] + resp[1]) == max_count

    # with obsolete changeset
    wrapper.command('amend', message=b'amended')
    assert do_rpc(b"branch/default", top_ctx.hex()) == [2, 1]


def test_count_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def do_rpc(revision, **kwargs):
        kwargs['repository'] = grpc_repo
        if revision is not None:
            kwargs['revision'] = revision
        return grpc_stub.CountCommits(CountCommitsRequest(**kwargs)).count

    # prepare repo as:
    #
    #   2 (branch/default)
    #   |
    #   1
    #   |  3 (topic/default/feature)
    #   | /
    #   0
    #
    ctx0 = wrapper.write_commit('foo')
    ctx1 = wrapper.write_commit('bar', parent=ctx0)
    wrapper.write_commit('baz', parent=ctx1)
    topic_hex = wrapper.write_commit('animals',
                                     topic='feature',
                                     parent=ctx0).hex()

    # simplest calls
    assert do_rpc(b'branch/default') == 3
    assert do_rpc(b'topic/default/feature') == 2
    assert do_rpc(topic_hex) == 2

    # when no revision passed, return total commits in repo
    assert do_rpc(None) == 4
    assert do_rpc(None, max_count=2) == 2

    # range notation
    assert do_rpc(b'branch/default..topic/default/feature') == 1
    assert do_rpc(b'topic/default/feature..branch/default') == 2

    # cases of revision not found
    assert all(do_rpc(revision) == 0
               for revision in (b'branch/default..unknown',
                                b'unknown..topic/default/feature',
                                b'unknown'))

    # obsolescence
    wrapper.command('amend', message=b'amended')
    assert do_rpc(topic_hex) == 2
    assert do_rpc(b'branch/default..' + topic_hex) == 1
    assert do_rpc(topic_hex + b'..branch/default') == 2


def test_last_commit_for_path(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # prepare repo as:
    #
    #   1 (branch/default) changes 'foo'
    #   |
    #   |  2 (branch/other) creates 'sub/bar'
    #   | /
    #   0 creates 'foo'
    #
    ctx = wrapper.write_commit('foo')
    ctx1 = wrapper.write_commit('foo')
    # TODO should be done by testhelpers!
    (wrapper.path / 'sub').mkdir()
    ctx2 = wrapper.write_commit('sub/bar', branch='other', parent=ctx)

    def do_rpc(revision, path):
        """Call the method, returning directly commit.id, as bytes"""
        request = LastCommitForPathRequest(repository=grpc_repo,
                                           revision=revision,
                                           path=path)
        return pycompat.sysbytes(
            grpc_stub.LastCommitForPath(request).commit.id)

    assert do_rpc(revision=b'branch/default', path=b'foo') == ctx1.hex()
    assert do_rpc(revision=b'branch/other', path=b'foo') == ctx.hex()
    assert do_rpc(revision=ctx2.hex(), path=b'foo') == ctx.hex()
    assert not do_rpc(revision=b'branch/default', path=b'sub/bar')
    assert do_rpc(revision=b'branch/other', path=b'sub/bar') == ctx2.hex()
    # recursive directory matching (see Rails tests for validation
    # that we must match on directories)
    assert do_rpc(revision=b'branch/other', path=b'sub') == ctx2.hex()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx2.obsolete()
    assert do_rpc(revision=ctx2.hex(), path=b'foo') == ctx.hex()


def test_list_commits_by_oid(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def do_rpc(oids):
        request = ListCommitsByOidRequest(repository=grpc_repo,
                                          oid=oids)
        resp = grpc_stub.ListCommitsByOid(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]

    ctx = wrapper.write_commit('foo')
    ctx2 = wrapper.write_commit('foo')

    # with 39, chances of collision are very thin and it still demonstrates
    # that prefix lookup works
    short = ctx.hex()[:39]
    short2 = ctx2.hex()[:39]

    assert do_rpc([short]) == [ctx.hex()]
    assert do_rpc([short, short2]) == [ctx.hex(), ctx2.hex()]

    assert do_rpc([]) == []

    unknown_sha = "6caf" * 9  # prefix of length 36, very unlikey to match
    assert do_rpc([unknown_sha]) == []
    assert do_rpc([unknown_sha, short]) == [ctx.hex()]

    # heptapod#640: obsolete changeset given by its full hash
    wrapper.command('amend', message=b'amended')
    assert do_rpc([ctx2.hex()]) == [ctx2.hex()]


def test_get_commit_messages(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # prepare repo as:
    #
    #   1 (branch/default) changes 'foo'
    #   |
    #   0 creates 'foo'
    #
    ctx0 = wrapper.write_commit('foo', message=b'added foo')
    ctx1 = wrapper.write_commit('foo', message=b'changes foo')
    sha0, sha1 = ctx0.hex(), ctx1.hex()

    def do_rpc(commit_ids):
        request = GetCommitMessagesRequest(repository=grpc_repo,
                                           commit_ids=commit_ids)
        response = grpc_stub.GetCommitMessages(request)
        results = {}
        for resp in response:
            commit_id = resp.commit_id
            if commit_id:
                results[commit_id] = resp.message
        return list(results.values())
    assert do_rpc([sha1, sha0]) == [b"changes foo", b"added foo"]
    assert do_rpc([sha1]) == [b"changes foo"]

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc([sha1, '12ca34de' * 5, sha0])
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'object not found' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx1.obsolete()
    assert do_rpc([sha1]) == [b"changes foo"]


def test_commit_stats(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # repo structure:
    #
    #   2 Removed two lines
    #   |
    #   1 added one line, removed one
    #   |
    #   0 added foo
    #
    sha0 = wrapper.commit_file(
        'foo',
        content="First line\nSecond line\nThird line\n",
        message=b'added foo'
    ).hex()

    sha1 = wrapper.commit_file(
        'foo',
        content="Second line\nThird line\nFourth line\n",
        message=b'added one line, removed one'
    ).hex()

    ctx2 = wrapper.commit_file(
        'foo',
        content="Fourth line\n",
        message=b'Removed two lines'
    )
    sha2 = ctx2.hex()

    def do_rpc(rev):
        request = CommitStatsRequest(repository=grpc_repo,
                                     revision=rev)
        resp = grpc_stub.CommitStats(request)
        return resp.additions, resp.deletions

    assert do_rpc(sha0) == (3, 0)
    assert do_rpc(sha1) == (1, 1)
    assert do_rpc(sha2) == (0, 2)

    # with unknown revision
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(b"23fire32" * 5)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'object not found' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx2.obsolete()
    assert do_rpc(sha2) == (0, 2)


def test_tree_entry(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx0 = wrapper.write_commit('foo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    (sub / 'ba2').chmod(0o755)
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2'],
                          message="zebar", add_remove=True)

    def do_rpc(path, limit=0, max_size=0, revision=ctx1.hex()):
        request = TreeEntryRequest(repository=grpc_repo,
                                   revision=revision,
                                   limit=limit,
                                   max_size=max_size,
                                   path=path)
        resp = grpc_stub.TreeEntry(request)
        return [r for r in resp]

    def rpc_single_response(*args, **kwargs):
        resps = do_rpc(*args, **kwargs)
        assert len(resps) == 1
        return resps[0]

    for rev in (ctx1.hex(), b'branch/default'):
        resp = rpc_single_response(b'sub/bar', revision=rev)
        assert resp.data == b'bar content'
        assert resp.mode == 0o100644
        assert resp.type == TreeEntryResponse.ObjectType.BLOB

    resp = rpc_single_response(b'sub')
    assert resp.type == TreeEntryResponse.ObjectType.TREE
    assert resp.mode == 0o40000

    resp = rpc_single_response(b'sub/ba2', limit=3)
    assert resp.type == TreeEntryResponse.ObjectType.BLOB
    assert resp.data == b'ba2'

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(b'foo', revision=ctx0.hex(), max_size=5)
    assert exc_info.value.code() == grpc.StatusCode.FAILED_PRECONDITION
    err_details = exc_info.value.details()
    assert 'bigger than the maximum allowed size (5)' in err_details

    # revision or file not found
    resp = rpc_single_response(b'not/there')
    assert not resp.data
    assert not resp.oid
    resp = rpc_single_response(b'foo', revision=b'branch/unknown')
    assert not resp.data
    assert not resp.oid

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx1.obsolete()
    resp = rpc_single_response(b'sub/bar', revision=rev)
    assert resp.data == b'bar content'
    assert resp.mode == 0o100644
    assert resp.type == TreeEntryResponse.ObjectType.BLOB


def test_get_tree_entries(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    repo = wrapper.repo

    wrapper.write_commit('foo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    (sub / 'ba2').chmod(0o755)
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2'],
                          message="zebar", add_remove=True)

    SortBy = GetTreeEntriesRequest.SortBy

    def do_rpc(path, revision=ctx1.hex(),
               limit=10, page_token='',
               sort=SortBy.DEFAULT,
               recursive=False):
        pagination_params = PaginationParameter(limit=limit,
                                                page_token=page_token)
        request = GetTreeEntriesRequest(repository=grpc_repo,
                                        revision=revision,
                                        path=path,
                                        pagination_params=pagination_params,
                                        sort=sort,
                                        recursive=recursive)
        entries = []
        cursor = None  # loop below can be empty
        for resp in grpc_stub.GetTreeEntries(request):
            entries.extend(resp.entries)
            # same implementation as on the Rails side, less robust than
            # initial version in order to reproduce hgitaly#91
            if resp.HasField('pagination_cursor'):
                cursor = resp.pagination_cursor.next_cursor

        return entries, cursor

    ctx1_oid = ctx1.hex().decode()
    root1_oid = tree_oid(repo, ctx1_oid, b'')
    bar_default = TreeEntry(path=b'sub/bar',
                            flat_path=b'sub/bar',
                            mode=0o100644,
                            oid=blob_oid(repo, ctx1_oid, b'sub/bar'),
                            commit_oid=ctx1_oid,
                            root_oid=root1_oid,
                            )
    ba2_default = TreeEntry(path=b'sub/ba2',
                            flat_path=b'sub/ba2',
                            mode=0o100755,
                            oid=blob_oid(repo, ctx1_oid, b'sub/ba2'),
                            commit_oid=ctx1_oid,
                            root_oid=root1_oid,
                            )
    foo_default = TreeEntry(path=b'foo',
                            flat_path=b'foo',
                            mode=0o100644,
                            oid=blob_oid(repo, ctx1_oid, b'foo'),
                            commit_oid=ctx1_oid,
                            root_oid=root1_oid,
                            )
    sub_default = TreeEntry(path=b'sub',
                            flat_path=b'sub',
                            mode=0o40000,
                            type=TreeEntry.EntryType.TREE,
                            oid=blob_oid(repo, ctx1_oid, b'sub'),
                            commit_oid=ctx1_oid,
                            root_oid=root1_oid,
                            )

    assert do_rpc(b'sub') == ([ba2_default, bar_default], '')

    assert do_rpc(b'.', recursive=False)[0] == [foo_default, sub_default]
    # Note for recursive call: that top-level paths are before deeper
    # ones is a mere coincidence.
    expected_recursive = [foo_default, sub_default, ba2_default, bar_default]
    for entry in expected_recursive:
        entry.flat_path = b''
    assert do_rpc(b'.', recursive=True)[0] == expected_recursive

    assert do_rpc(b'.', recursive=True, limit=0)[0] == []
    assert do_rpc(b'.', recursive=True, limit=-1)[0] == expected_recursive

    limited, cursor = do_rpc(b'.', recursive=True, limit=2)
    assert limited == expected_recursive[:2]
    assert cursor == expected_recursive[1].oid
    assert do_rpc(b'.', recursive=True,
                  page_token=cursor)[0] == expected_recursive[2:]

    assert do_rpc(b'.', recursive=True, sort=SortBy.TREES_FIRST)[0] == [
        sub_default, foo_default, ba2_default, bar_default]

    invalid_cursor = 'this is not an OID'
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(b'.', page_token=invalid_cursor)
    assert exc_info.value.code() == grpc.StatusCode.UNKNOWN
    assert invalid_cursor in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx1.obsolete()
    assert do_rpc(b'.', revision=ctx1.hex(),
                  recursive=True)[0] == expected_recursive


def test_list_last_commits_for_tree(grpc_channel, server_repos_root):

    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    ctx0 = wrapper.write_commit('foo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2'],
                          message="zebar", add_remove=True)
    ctx2 = wrapper.write_commit('sub/bar')
    ctx3 = wrapper.write_commit('foo', parent=ctx1, branch='other')
    ctx4 = wrapper.write_commit('oof')

    sha0 = ctx0.hex().decode()
    sha1 = ctx1.hex().decode()
    sha2 = ctx2.hex().decode()
    sha3 = ctx3.hex().decode()
    sha4 = ctx4.hex().decode()

    def do_rpc(rev, path, offset=0, limit=None):
        request = ListLastCommitsForTreeRequest(
            repository=grpc_repo,
            offset=offset,
            limit=1000 if limit is None else limit,
            revision=rev,
            path=path)
        return [(cft.path_bytes, cft.commit.id)
                for chunk in grpc_stub.ListLastCommitsForTree(request)
                for cft in chunk.commits]

    assert do_rpc(sha2, b'sub/', limit=0) == []

    assert do_rpc(sha2, b'sub/') == [
        (b'sub/ba2', sha1),
        (b'sub/bar', sha2),
    ]

    # we need the trailing slash to trigger inspection of tree content
    assert do_rpc(sha2, b'sub') == [(b'sub', sha2)]
    assert do_rpc(sha2, b'sub', offset=1) == []

    # ...except for the root tree
    assert do_rpc(sha2, b'') == [
        (b'sub', sha2),
        (b'foo', sha0),
    ]

    # other spellings of the root tree
    assert do_rpc(sha2, b'.') == do_rpc(sha2, b'')
    assert do_rpc(sha2, b'/') == do_rpc(sha2, b'')
    assert do_rpc(sha2, b'./') == do_rpc(sha2, b'')

    # usage of revision instead of a sha
    assert do_rpc('branch/default', b'sub') == do_rpc(sha2, b'sub')

    assert do_rpc(sha3, b'sub/') == [
        (b'sub/ba2', sha1),
        (b'sub/bar', sha1),
    ]

    assert do_rpc(sha3, b'.') == [
        (b'sub', sha1),
        (b'foo', sha3),
    ]

    # for offset, limit tests we'll use sha4 to have more content.
    assert do_rpc(sha4, b'', limit=4) == [
        (b'sub', sha1),
        (b'foo', sha3),
        (b'oof', sha4),
    ]

    assert do_rpc(sha4, b'', limit=2) == [
        (b'sub', sha1),
        (b'foo', sha3),
    ]

    assert do_rpc(sha4, b'', offset=1, limit=2) == [
        (b'foo', sha3),
        (b'oof', sha4),
    ]

    unknown_sha = b'be0123ef' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(unknown_sha, b'')
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'exit status 128' in exc_info.value.details()

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha1, b'', limit=-1)
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'limit' in exc_info.value.details()

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha1, b'', offset=-1)
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'offset' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx4.obsolete()
    assert do_rpc(sha4, b'', limit=2) == [
        (b'sub', sha1),
        (b'foo', sha3),
    ]


def test_raw_blame(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    # repo structure:
    #
    #   2 updated both lines
    #   |
    #   1 added one more line
    #   |
    #   0 added first line to foo
    #
    sha0 = wrapper.commit_file(
        'foo', message=b'zefoo',
        content='Second line\n'
                'Third line\n'
    ).hex()

    sha1 = wrapper.commit_file(
        'foo', message=b'zefoo',
        content='First line\n'
                'Second line\n'
                'Third line\n'
                'Forth line\n'
    ).hex()

    def do_rpc(rev, path):
        request = RawBlameRequest(repository=grpc_repo,
                                  revision=rev,
                                  path=path)
        response = grpc_stub.RawBlame(request)
        data = [resp.data for resp in response]
        return b''.join(data)

    assert do_rpc(sha0, b'foo') == (
        b'%s 1 1\n'
        b'\tSecond line\n'
        b'%s 2 2\n'
        b'\tThird line\n' % (sha0, sha0)
    )

    expected_rev1 = (
        b'%s 1 1\n'
        b'\tFirst line\n'
        b'%s 1 2\n'
        b'\tSecond line\n'
        b'%s 2 3\n'
        b'\tThird line\n'
        b'%s 4 4\n'
        b'\tForth line\n' % (sha1, sha0, sha0, sha1)
    )
    assert do_rpc(sha1, b'foo') == expected_rev1

    # with unknown revision
    assert do_rpc(b"23fire32" * 5, b'foo') == b''

    # with empty path
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha0, b'')
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'RawBlame: empty Path' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert do_rpc(sha1, b'foo') == expected_rev1


def test_list_files(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    sha0 = wrapper.commit_file('foo').hex()
    sha1 = wrapper.commit_file('bar').hex()
    sha2 = wrapper.commit_file('zoo').hex()

    def do_rpc(rev):
        request = ListFilesRequest(repository=grpc_repo,
                                   revision=rev)
        response = grpc_stub.ListFiles(request)
        final = []
        for resp in response:
            final.extend(resp.paths)
        return final

    assert do_rpc(sha0) == [b'foo']
    assert do_rpc(sha1) == [b'bar', b'foo']
    assert do_rpc(sha2) == [b'bar', b'foo', b'zoo']

    # with unknown revision
    assert do_rpc(b"23fire32" * 5) == []

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert do_rpc(sha2) == [b'bar', b'foo', b'zoo']


def test_list_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # see graph in Gitaly Comparison test
    ctx0 = wrapper.commit_file('foo')
    sha0 = ctx0.hex()
    ctx1 = wrapper.commit_file('foo', topic='sampletop')
    wrapper.update(ctx0.rev())
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    ts = int(time.time())
    sha2 = wrapper.commit([b'foo', b'zoo'],
                          message=b"rename foo to zoo",
                          utc_timestamp=ts - 10,).hex()
    ctx3 = wrapper.write_commit('animals', branch='stable', parent=ctx0,
                                utc_timestamp=ts+10,
                                user='testuser <testuser@heptapod.test')
    sha3 = ctx3.hex()
    wrapper.update(2)
    ctx4 = wrapper.merge_commit(ctx3, message=b'merge with stable')
    sha4 = ctx4.hex()

    def caret(ctx):
        return b'^' + ctx.hex()

    def do_rpc(*revisions, limit=None, page_token=None, **kw):
        if limit is None and page_token is None:
            pagination = None
        else:
            pagination = PaginationParameter(limit=limit,
                                             page_token=page_token)

        request = ListCommitsRequest(repository=grpc_repo,
                                     revisions=revisions,
                                     pagination_params=pagination,
                                     **kw,
                                     )

        resp = grpc_stub.ListCommits(request)
        return [c.id.encode('ascii') for chunk in resp for c in chunk.commits]

    assert do_rpc(sha4, caret(ctx1)) == [sha4, sha3, sha2]
    assert do_rpc(sha4, caret(ctx1), reverse=True) == [sha2, sha3, sha4]

    # limit and page token
    assert do_rpc(sha4, limit=2) == [sha4, sha3]
    assert do_rpc(sha4, limit=10, page_token=sha2) == [ctx0.hex()]

    # orderings
    Order = ListCommitsRequest.Order
    assert do_rpc(sha4, order=Order.TOPO) == [sha4, sha3, sha2, sha0]
    assert do_rpc(sha4, order=Order.DATE) == [sha2, sha0, sha4, sha3]

    # unknown revision
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(b'branch/unknown')

    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'branch/unknown' in exc_info.value.details()

    # invalid arguments
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc()
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'revision' in exc_info.value.details()

    # with obsolete changeset
    wrapper.command('amend', message=b'amended')
    assert ctx4.obsolete()
    assert do_rpc(sha4, limit=2) == [sha4, sha3]
