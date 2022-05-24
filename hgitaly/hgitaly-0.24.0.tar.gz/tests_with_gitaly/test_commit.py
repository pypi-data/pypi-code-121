# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
import pytest
import re
import time
from hgitaly.stub.shared_pb2 import (
    PaginationParameter,
)
from hgitaly.stub.commit_pb2 import (
    FindCommitsRequest,
    ListCommitsRequest,
    ListFilesRequest,
    ListLastCommitsForTreeRequest,
    RawBlameRequest,
)
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub
from google.protobuf.timestamp_pb2 import Timestamp

from . import skip_comparison_tests
from .comparison import (
    normalize_commit_message,
)
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_compare_list_last_commits_for_tree(gitaly_comparison):
    fixture = gitaly_comparison
    git_repo = fixture.git_repo

    wrapper = fixture.hg_repo_wrapper
    ctx0 = wrapper.write_commit('foo', message="Some foo")
    git_shas = {
        ctx0.hex(): git_repo.branches()[b'branch/default']['sha'],
    }

    sub = (wrapper.path / 'sub')
    sub.mkdir()
    subdir = (sub / 'dir')
    subdir.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    (subdir / 'bar').write_text('bar content')
    (subdir / 'ba2').write_text('ba2 content')
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2',
                                     'sub/dir/bar', 'sub/dir/ba2'],
                          message="ze\nbar", add_remove=True)
    git_shas[ctx1.hex()] = git_repo.branches()[b'branch/default']['sha']
    ctx2 = wrapper.write_commit('sub/bar', message='default head')
    ctx3 = wrapper.write_commit('foo', parent=ctx1, branch='other',
                                message='other head')

    # mirror worked
    git_branches = git_repo.branches()
    assert set(git_branches) == {b'branch/default', b'branch/other'}

    def response_ignores(rpc_helper, responses, **kw):
        for resp in responses:
            for commit_for_tree in resp.commits:
                normalize_commit_message(commit_for_tree.commit)

    rpc_helper = fixture.rpc_helper(stub_cls=CommitServiceStub,
                                    method_name='ListLastCommitsForTree',
                                    streaming=True,
                                    request_cls=ListLastCommitsForTreeRequest,
                                    request_defaults=dict(limit=1000),
                                    request_sha_attrs=['revision'],
                                    response_sha_attrs=[
                                        'commits[].commit.id',
                                        'commits[].commit.parent_ids[]',
                                        ],
                                    normalizer=response_ignores,
                                    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    for path in (b'sub/dir', b'sub/dir/', b'', b'.', b'/', b'./',
                 b'sub', b'sub/', b'foo'):
        for rev in ('branch/default', 'branch/other', ctx2.hex(), ctx3.hex()):
            assert_compare(revision=rev, path=path)

    assert_compare(revision='branch/default', path=b'sub', offset=1)

    # for a bunch of assertions that aren't about revision nor path
    common_args = dict(revision=ctx2.hex(), path=b'')
    assert_compare(limit=0, **common_args)
    assert_compare_errors(limit=-1, **common_args)
    assert_compare_errors(limit=10, offset=-1, **common_args)

    # error won't be due to invalidity as a SHA, but because commit doesn't
    # exist (let's not depend on Gitaly accepting symbolic revisions, here)
    assert_compare_errors(revision=b'be0123ef' * 5, path=b'')


def test_compare_raw_blame(gitaly_comparison):
    fixture = gitaly_comparison

    wrapper = fixture.hg_repo_wrapper
    ctx0 = wrapper.commit_file('foo',
                               content='second_line\n'
                                       'third_line\n')
    ctx1 = wrapper.commit_file('foo',
                               content='first_line\n'
                                       'second_line\n'
                                       'third_line\n'
                                       'forth_line\n')

    RAW_BLAME_LINE_REGEXP = re.compile(br'(\w{40}) (\d+) (\d+)')

    def convert_chunk(rpc_helper, chunk, vcs):
        lines = chunk.splitlines(True)
        final = []
        for line in lines:
            hash_line = RAW_BLAME_LINE_REGEXP.match(line)
            if hash_line is not None:
                hash_id = hash_line.group(1)
                if vcs == 'hg':
                    hash_id = rpc_helper.hg2git(hash_id)
                line_no = hash_line.group(2)
                old_line_no = hash_line.group(2)
                final.append((hash_id, line_no, old_line_no))
            elif line.startswith(b'\t'):
                final.append(line)
        return final

    def normalizer(rpc_helper, responses, vcs=None):
        for i, chunk in enumerate(responses):
            responses[i] = convert_chunk(rpc_helper, chunk.data, vcs)

    rpc_helper = fixture.rpc_helper(
        stub_cls=CommitServiceStub,
        method_name='RawBlame',
        request_cls=RawBlameRequest,
        request_sha_attrs=['revision'],
        streaming=True,
        normalizer=normalizer,
    )

    rpc_helper.assert_compare(revision=ctx0.hex(), path=b'foo')
    rpc_helper.assert_compare(revision=ctx1.hex(), path=b'foo')

    # error cases with empty path
    rpc_helper.assert_compare_errors(revision=ctx1.hex(), path=b'')


def test_compare_list_files(gitaly_comparison):
    fixture = gitaly_comparison
    git_repo = fixture.git_repo

    wrapper = fixture.hg_repo_wrapper
    ctx0 = wrapper.write_commit('foo', message="Some foo")

    sub = (wrapper.path / 'sub')
    sub.mkdir()
    subdir = (sub / 'dir')
    subdir.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    (subdir / 'bar').write_text('bar content')
    (subdir / 'ba2').write_text('ba2 content')
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    ctx1 = wrapper.commit(rel_paths=['sub/bar', 'sub/ba2',
                                     'sub/dir/bar', 'sub/dir/ba2'],
                          message="zebar", add_remove=True)
    ctx2 = wrapper.write_commit('sub/bar', message='default head')
    ctx3 = wrapper.write_commit('zoo', parent=ctx0, branch='other',
                                message='other head')

    # mirror worked
    git_branches = git_repo.branches()
    assert set(git_branches) == {b'branch/default', b'branch/other'}

    rpc_helper = fixture.rpc_helper(
        stub_cls=CommitServiceStub,
        method_name='ListFiles',
        request_cls=ListFilesRequest,
        streaming=True,
        request_sha_attrs=['revision'],
    )

    not_exists = b'65face65' * 5
    for rev in [ctx0.hex(), ctx1.hex(), ctx2.hex(), ctx3.hex(),
                not_exists, b'branch/default', b'branch/other']:
        rpc_helper.assert_compare(revision=rev)


def test_compare_find_commits(gitaly_comparison):
    fixture = gitaly_comparison
    wrapper = fixture.hg_repo_wrapper

    def normalizer(rpc_helper, responses, **kw):
        # Sorting is for the special cases where, we have two
        # commits diverging and Git order the commits arbitrarily
        # for e.g.
        #
        #  B
        #  |  C          Here, if selecting from bottom to top, order
        #  | /           can be: (A, B, C) or (A, C, B)
        #  A
        #
        # We actually sort inside each chunk instead of the whole, but
        # that should be enough.
        if rpc_helper.sorted:
            for chunk in responses:
                chunk.commits.sort(key=lambda c: c.id)

        for chunk in responses:
            for commit in chunk.commits:
                normalize_commit_message(commit)

    rpc_helper = fixture.rpc_helper(
        stub_cls=CommitServiceStub,
        method_name='FindCommits',
        request_cls=FindCommitsRequest,
        streaming=True,
        request_defaults=dict(limit=10),
        request_sha_attrs=['revision'],
        response_sha_attrs=['commits[].id', 'commits[].parent_ids[]'],
        normalizer=normalizer,
        )
    rpc_helper.sorted = False

    @contextmanager
    def sorted_comparison():
        orig = rpc_helper.sorted
        rpc_helper.sorted = True
        yield
        rpc_helper.sorted = orig

    assert_compare = rpc_helper.assert_compare

    assert_compare(revision=b'HEAD')
    del fixture.hg_git  # invalidate GitHandler instance (for its hg->git map)

    # set_default_gitlab_branch(wrapper.repo, b'branch/default')
    # prepare repo as:
    #
    #   @    4 (branch/default) merge with stable
    #   |\
    #   | o  3 creates 'animal' (branch/stable)
    #   | |
    #   o |  2 rename 'foo' to 'zoo' (user: testuser)
    #   |/
    #   | 1 changes 'foo' (topic: sampletop)
    #   |/
    #   o  0  creates 'foo'
    #

    ctx0 = wrapper.commit_file('foo')
    ctx1 = wrapper.commit_file('foo', topic='sampletop')
    wrapper.update(ctx0.rev())
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    ctx2 = wrapper.commit([b'foo', b'zoo'], message=b"rename foo to zoo")
    ts = int(time.time())
    ctx3 = wrapper.write_commit('animals', branch='stable', parent=ctx0,
                                utc_timestamp=ts+10,
                                user='testuser <testuser@heptapod.test')
    wrapper.update(2)
    ctx4 = wrapper.merge_commit(ctx3, message=b'merge with stable',
                                utc_timestamp=ts+20)

    # when `revision` is provided as <revspec>
    with sorted_comparison():
        all_revs = [ctx0.hex(), ctx1.hex(), ctx2.hex(), ctx3.hex(), ctx4.hex()]
        for range_str in (b'..', b'...'):
            for r1 in all_revs:
                for r2 in all_revs:
                    assert_compare(revision=r1 + range_str + r2)

    # when `revision` is provided as a ref to a single commit
    refs = [b'', ctx0.hex(), b'topic/default/sampletop', ctx2.hex(),
            b'branch/stable', b'branch/default', b'HEAD']
    for ref in refs:
        rpc_helper.assert_compare(revision=ref)

    # with `path` and `follow` options
    test_paths = [
        # Note: we are not including [b'foo'] here, because of a special case:
        # in a rename-cset (foo -> zoo), Git consider the cset but Hg doesn't,
        # as 'foo' is not present in rename-cset.
        [b'zoo'],
        [b'foo', b'zoo'],
    ]
    for follow in [True, False]:
        for paths in test_paths:
            if len(paths) > 1:
                # In Git, 'follow' doesn't work with multiple paths
                follow = False
            rpc_helper.assert_compare(paths=paths, follow=follow)

    # with simple options
    with sorted_comparison():
        assert_compare(all=True)
    assert_compare(author=b'testuser')
    assert_compare(skip_merges=True)

    # with pagination options
    for limit in range(0, 5):
        for offset in range(0, 5):
            assert_compare(offset=offset, limit=limit)
    assert_compare(order=FindCommitsRequest.Order.TOPO)

    # with `after` and `before` options for dates
    date1, date2 = Timestamp(), Timestamp()
    date1.FromSeconds(ts+10)
    date2.FromSeconds(ts+20)
    for date in [date1, date2]:
        assert_compare(after=date)
        assert_compare(before=date)
        assert_compare(before=date, after=date)


def test_compare_list_commits(gitaly_comparison):
    fixture = gitaly_comparison

    wrapper = fixture.hg_repo_wrapper
    # set_default_gitlab_branch(wrapper.repo, b'branch/default')
    # prepare repo as:
    #
    #   @    4 (branch/default) merge with stable
    #   |\
    #   | o  3 creates 'animal' (branch/stable)
    #   | |
    #   o |  2 rename 'foo' to 'zoo' (user: testuser)
    #   |/
    #   | 1 changes 'foo' (topic: sampletop)
    #   |/
    #   o  0  creates 'foo'
    #

    ctx0 = wrapper.commit_file('foo')
    ctx1 = wrapper.commit_file('foo', topic='sampletop')
    wrapper.update(ctx0.rev())
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    ts = int(time.time())
    ctx2 = wrapper.commit([b'foo', b'zoo'],
                          message=b"rename foo to zoo",
                          utc_timestamp=ts - 10)
    ctx3 = wrapper.write_commit('animals', branch='stable', parent=ctx0,
                                utc_timestamp=ts + 10,
                                user='testuser <testuser@heptapod.test')
    wrapper.update(2)
    ctx4 = wrapper.merge_commit(ctx3, message=b'merge with stable',
                                utc_timestamp=ts+20)

    def normalizer(rpc_helper, responses, **kw):
        for chunk in responses:
            for commit in chunk.commits:
                normalize_commit_message(commit)

    rpc_helper = fixture.rpc_helper(
        stub_cls=CommitServiceStub,
        method_name='ListCommits',
        request_cls=ListCommitsRequest,
        streaming=True,
        request_defaults=dict(
            pagination_params=PaginationParameter(limit=10)),
        request_sha_attrs=['revision'],
        response_sha_attrs=['commits[].id', 'commits[].parent_ids[]'],
        normalizer=normalizer,
        )
    rpc_helper.sorted = False

    def request_kwargs_to_git(hg_kwargs):
        """Replace Mercurial SHAs by their Git counterparts.

        The format of the ``revisions`` parameter is too specific to
        be provided directly by :class:`RpcHelper`
        """
        git_kwargs = hg_kwargs.copy()
        revisions = hg_kwargs.get('revisions')
        if revisions is None:
            return git_kwargs

        git_kwargs['revisions'] = git_revisions = []
        for rev in revisions:
            if rev.startswith(b'^'):
                git_rev = b'^' + rpc_helper.revspec_to_git(rev[1:])
            else:
                git_rev = rpc_helper.revspec_to_git(rev)
            git_revisions.append(git_rev)

        pagination = hg_kwargs.get('pagination_params')
        if pagination is not None and pagination.page_token:
            git_kwargs['pagination_params'] = PaginationParameter(
                limit=pagination.limit,
                page_token=rpc_helper.revspec_to_git(pagination.page_token)
            )

        return git_kwargs

    rpc_helper.request_kwargs_to_git = request_kwargs_to_git

    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    def caret(ctx):
        return b'^' + ctx.hex()

    assert_compare(revisions=[ctx4.hex(), caret(ctx1)])
    assert_compare(revisions=[ctx4.hex(), caret(ctx1)], reverse=True)
    # interpretation of several exclusions
    assert_compare(revisions=[ctx4.hex(), caret(ctx1), caret(ctx2)])

    # orderings
    #
    # Comparison is limited because Mercurial orderings don't exactly
    # match Git's. See docstring of the `ListCommit` method for details.
    # Notably we can't compare the date ordering (or we would cheat by
    # using special cases where they coincide, which is worse than no test)
    Order = ListCommitsRequest.Order
    assert_compare(revisions=[ctx4.hex()], order=Order.TOPO)

    # limit and page token
    assert_compare(revisions=[ctx4.hex()],
                   order=Order.TOPO,
                   pagination_params=PaginationParameter(limit=2))

    # starting over *after* the emission of ctx2 does not mean
    # completing the just-tested limit request, which stopped right before
    # emitting ctx2 (in case someone inspects the inner values and is puzzled
    # not to see all ancestors of ctx4).
    assert_compare(
        revisions=[ctx4.hex()],
        order=Order.TOPO,
        pagination_params=PaginationParameter(limit=10,
                                              page_token=ctx2.hex()))

    # unknown revision
    assert_compare_errors(revisions=[b'1234' * 10], same_details=False)

    # invalid calls
    assert_compare_errors(order=Order.TOPO)
