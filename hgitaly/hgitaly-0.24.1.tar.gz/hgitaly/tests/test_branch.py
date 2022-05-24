# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import re
import time

from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from ..branch import (
    BranchSortBy,
    ensure_gitlab_branches_state_file,
    gitlab_branch_head,
    gitlab_branches_matcher,
    iter_gitlab_branches,
    iter_gitlab_branches_as_refs,
    iter_gitlab_branches_matching,
    sorted_gitlab_branches_as_refs,
)

from hgext3rd.heptapod.branch import (
    GITLAB_BRANCHES_MISSING,
    gitlab_branches,
    set_default_gitlab_branch,
    write_gitlab_branches,
)


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(topic=''),
                                 ))


def test_iter_no_state_file(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    default_branch = b'branch/default'
    default_branch_ref = b'refs/heads/branch/default'

    base = wrapper.write_commit('foo')
    base_sha = base.hex().decode()

    assert list(iter_gitlab_branches(repo)) == [(default_branch, base)]
    assert list(iter_gitlab_branches(repo, deref=False)) == [
                (default_branch, base_sha)]

    assert list(iter_gitlab_branches_as_refs(repo)) == [
        (default_branch_ref, base)]
    assert list(iter_gitlab_branches_as_refs(repo, deref=False)
                ) == [(default_branch_ref, base_sha)]

    another = wrapper.write_commit('bar', branch='another',
                                   utc_timestamp=time.time() + 10)
    another_sha = another.hex().decode()
    another_branch_ref = b'refs/heads/branch/another'
    assert list(sorted_gitlab_branches_as_refs(
        repo, sort_by=BranchSortBy.FULL_REF_NAME
    )) == [
        (another_branch_ref, another),
        (default_branch_ref, base),
    ]
    assert list(sorted_gitlab_branches_as_refs(
        repo,
        sort_by=BranchSortBy.FULL_REF_NAME,
        deref=False,
    )) == [
        (another_branch_ref, another_sha),
        (default_branch_ref, base_sha),
    ]
    assert list(sorted_gitlab_branches_as_refs(
        repo,
        sort_by=BranchSortBy.UPDATED_ASC,
        deref=True,
    )) == [
        (default_branch_ref, base),
        (another_branch_ref, another),
    ]
    assert list(sorted_gitlab_branches_as_refs(
        repo,
        sort_by=BranchSortBy.UPDATED_ASC,
        deref=False,
    )) == [
        (default_branch_ref, base_sha),
        (another_branch_ref, another_sha),
    ]
    assert list(sorted_gitlab_branches_as_refs(
        repo,
        sort_by=BranchSortBy.UPDATED_DESC,
    )) == [
        (another_branch_ref, another),
        (default_branch_ref, base),
    ]

    assert list(sorted_gitlab_branches_as_refs(
        repo,
        sort_by=BranchSortBy.UPDATED_ASC,
        after=default_branch_ref,
    )) == [
        (another_branch_ref, another),
    ]


def test_named_branch_multiple_heads(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    default_branch = b'branch/default'

    # no head, no bookmark
    assert gitlab_branch_head(repo, default_branch) is None
    assert gitlab_branch_head(repo, b'zebook') is None

    # one head
    base = wrapper.write_commit('foo')
    assert gitlab_branch_head(repo, default_branch) == base
    assert list(iter_gitlab_branches(repo)) == [(default_branch, base)]

    # two heads, no bookmark
    head1 = wrapper.write_commit('foo')
    head2 = wrapper.write_commit('foo', parent=base)

    assert gitlab_branch_head(repo, default_branch) == head2
    assert set(iter_gitlab_branches(repo)) == {
        (default_branch, head2),
        (b'wild/' + head1.hex(), head1),
        (b'wild/' + head2.hex(), head2),
    }
    assert gitlab_branch_head(repo, b'wild/' + head1.hex()) == head1
    assert gitlab_branch_head(repo, b'wild/' + head2.hex()) == head2

    # one bookmarked head and one not bookmarked
    wrapper.command('bookmark', b'book2', rev=head2.hex())
    assert gitlab_branch_head(repo, default_branch) == head1
    assert set(iter_gitlab_branches(repo)) == {
        (default_branch, head1),
        (b'book2', head2),
    }
    assert gitlab_branch_head(repo, b'wild/' + head1.hex()) is None
    assert gitlab_branch_head(repo, b'wild/' + head2.hex()) is None
    assert gitlab_branch_head(repo, b'book2') == head2

    # all heads bookmarked
    wrapper.command('bookmark', b'book1', rev=head1.hex())
    assert gitlab_branch_head(repo, default_branch) is None
    assert set(iter_gitlab_branches(repo)) == {
        (b'book1', head1),
        (b'book2', head2),
    }

    # finally, a formally correct wild branch, with no corresponding changeset
    assert gitlab_branch_head(repo, b'wild/' + (b'cafe' * 10)) is None


def test_invalid_state_file_entry(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    # invalid entry is just ignored, be it in favor of other type of ref
    # or within the same type
    write_gitlab_branches(repo,
                          {b'branch/default': ctx.hex(),
                           b'invalid': b'1234beef' * 5})
    assert list(iter_gitlab_branches(repo)) == [(b'branch/default', ctx)]


def test_ensure_state_file(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    wrapper.write_commit('foo')

    assert gitlab_branches(repo) is GITLAB_BRANCHES_MISSING
    ensure_gitlab_branches_state_file(repo)
    # the state file creation stil relying on Git refs, since we didn't
    # convert anything, it's normal for the resulting dict of branches to
    # be empty (a later version would perhaps recompute it from HGitaly).
    assert gitlab_branches(repo) is not GITLAB_BRANCHES_MISSING


def test_bookmarks_not_shadowing_default_branch(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    base = wrapper.write_commit('foo')  # not strictly necessary
    head1 = wrapper.write_commit('foo')

    default_branch = b'branch/default'
    set_default_gitlab_branch(repo, default_branch)

    wrapper.command('bookmark', b'book1', rev=head1.hex())
    assert gitlab_branch_head(repo, default_branch) == head1

    head2 = wrapper.write_commit('foo', parent=base)
    wrapper.command('bookmark', b'book2', rev=head2.hex())

    assert gitlab_branch_head(repo, default_branch) == head2
    assert set(iter_gitlab_branches(repo)) == {
        (b'book1', head1),
        (b'book2', head2),
        (default_branch, head2)
    }


def test_gitlab_branches_state_file(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    base = wrapper.commit_file('foo')
    default = wrapper.commit_file('foo')
    topic = wrapper.commit_file('foo', parent=base, topic='zztop')

    write_gitlab_branches(wrapper.repo,
                          {b'branch/default': default.hex(),
                           b'topic/default/zztop': topic.hex(),
                           })

    assert gitlab_branch_head(repo, b'branch/default') == default
    assert gitlab_branch_head(repo, b'branch/typo') is None

    assert dict(iter_gitlab_branches(repo)) == {
        b'branch/default': default,
        b'topic/default/zztop': topic,
    }

    assert dict(iter_gitlab_branches(repo, deref=False)) == {
        b'branch/default': default.hex().decode(),
        b'topic/default/zztop': topic.hex().decode(),
    }

    # for self coverage (will be also covered by service tests)
    assert dict(iter_gitlab_branches_matching(repo, [b'branch/*'])) == {
        b'branch/default': default,
    }


def test_gitlab_branches_matcher():
    for glob_patterns, rx_pattern in (
            ([b'branch/default'], b'^(branch/default)$'),
            # simple wildcard
            ([b'branch/*'], b'^(branch/.*)$'),
            # escaping of regexp metacharacters
            ([b'branch/def.ult'], br'^(branch/def\.ult)$'),
            # several patterns
            ([b'branch/*', b'topic/dev*/*'],
             br'^(branch/.*)|(topic/dev.*/.*)$'),
            # incoming patterns is an iterator with one element
            (iter([b'somebranch']), b'^(somebranch)$'),
            # incoming patterns is an iterator with several elements
            (iter([b'some', b'other']), b'^(some)|(other)$'),
    ):
        assert gitlab_branches_matcher(glob_patterns) == re.compile(rx_pattern)

    # special case with no pattern still returns a regular expression that
    # matches anything

    rx = gitlab_branches_matcher(())
    assert rx.search(b'anything') is not None
    assert rx.match(b'anything') is not None
