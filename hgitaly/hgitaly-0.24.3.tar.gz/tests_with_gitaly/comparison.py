# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixture for Gitaly comparison tests based on Heptapod's Git mirroring."""
import attr
import contextlib
import functools
import pytest
import random

import grpc

from mercurial_testhelpers.util import as_bytes

from hggit.git_handler import GitHandler
from heptapod.testhelpers.gitlab import GitLabMirrorFixture
from hgitaly.stub.shared_pb2 import Repository


@attr.s
class GitalyComparison:
    hgitaly_channel = attr.ib()
    gitaly_channel = attr.ib()
    gitaly_repo = attr.ib()
    hgitaly_repo = attr.ib()
    gitlab_mirror = attr.ib()

    @property
    def hg_repo_wrapper(self):
        return self.gitlab_mirror.hg_repo_wrapper

    @property
    def git_repo(self):
        return self.gitlab_mirror.git_repo

    def rpc_helper(self, **kw):
        return RpcHelper(self, **kw)

    @functools.cached_property
    def hg_git(self):
        """The hg-git GitHandler instance, with SHA mapping preloaded.

        To invalidate this cached property, just delete it::
            del comparison.hg_git
        """
        hg_repo = self.hg_repo_wrapper.repo
        hg_git = GitHandler(hg_repo, hg_repo.ui)
        hg_git.load_map()
        return hg_git


@contextlib.contextmanager
def gitaly_comparison_fixture(server_repos_root,
                              gitaly_channel,
                              grpc_channel,
                              monkeypatch,
                              ):
    common_relative_path = 'repo-' + hex(random.getrandbits(64))[2:]
    storage = 'default'

    gitaly_repo = Repository(relative_path=common_relative_path + '.git',
                             storage_name=storage)
    hgitaly_repo = Repository(relative_path=common_relative_path + '.hg',
                              storage_name=storage)

    hg_config = dict(phases=dict(publish=False),
                     ui=dict(username='Hgitaly Tests <hgitaly@heptapod.test>'),
                     extensions={name: '' for name in ('evolve',
                                                       'hggit',
                                                       'topic',
                                                       'heptapod')})
    with GitLabMirrorFixture.init(
            server_repos_root / storage,
            monkeypatch,
            common_repo_name=common_relative_path,
            hg_config=hg_config,
    ) as mirror:
        # configuration must be written in HGRC file, because
        # HGitaly server will load the repository independently.
        mirror.hg_repo_wrapper.write_hgrc(hg_config)
        mirror.activate_mirror()
        yield GitalyComparison(
            hgitaly_channel=grpc_channel,
            hgitaly_repo=hgitaly_repo,
            gitaly_channel=gitaly_channel,
            gitaly_repo=gitaly_repo,
            gitlab_mirror=mirror,
        )


class RpcHelper:

    def __init__(self, comparison, stub_cls, method_name, request_cls,
                 repository_arg=True,
                 request_defaults=None,
                 request_sha_attrs=(),
                 response_sha_attrs=(),
                 normalizer=None,
                 streaming=False):
        self.comparison = comparison
        self.stubs = dict(git=stub_cls(comparison.gitaly_channel),
                          hg=stub_cls(comparison.hgitaly_channel))
        self.stub_cls = stub_cls
        self.method_name = method_name
        self.request_cls = request_cls
        self.streaming = streaming
        self.repository_arg = repository_arg

        self.request_defaults = request_defaults
        self.request_sha_attrs = request_sha_attrs
        self.response_sha_attrs = response_sha_attrs
        self.streaming = streaming
        self.normalizer = normalizer

    def rpc(self, vcs, **kwargs):
        if self.repository_arg:
            kwargs.setdefault('repository', self.comparison.gitaly_repo)
        request = self.request_cls(**kwargs)
        meth = getattr(self.stubs[vcs], self.method_name)
        if self.streaming:
            return [resp for resp in meth(request)]

        return meth(request)

    def hg2git(self, hg_sha):
        """Convert a Mercurial hex SHA to its counterpart SHA in Git repo.

        If not found in the Git Repo, the original SHA is returned, which
        is useful for tests about non existent commits.
        """
        # if hg_sha is None or not 40 bytes long it certainly won't
        # be found in the hg-git mapping, we don't need a special case
        # for that
        git_sha = self.comparison.hg_git.map_git_get(as_bytes(hg_sha))
        return hg_sha if git_sha is None else git_sha

    def request_kwargs_to_git(self, hg_kwargs):
        git_kwargs = hg_kwargs.copy()
        for sha_attr in self.request_sha_attrs:
            sha = hg_kwargs.get(sha_attr)
            if sha is None:
                continue
            git_kwargs[sha_attr] = self.revspec_to_git(sha)
        return git_kwargs

    def revspec_to_git(self, revspec):
        """Convert revision specifications, including ranges to Git.

        This is to be improved as new cases arise.
        """
        is_bytes = isinstance(revspec, bytes)
        symdiff_sep = b'...' if is_bytes else '...'
        only_sep = b'..' if is_bytes else '..'

        for sep in (symdiff_sep, only_sep):
            if sep in revspec:
                # hg2git() defaulting rule will let symbolic revisions, such
                # as refs go through untouched
                return sep.join(self.hg2git(rev)
                                for rev in revspec.split(sep))
        # TODO implement caret, tilda etc.
        return self.hg2git(revspec)

    def response_to_git(self, resp):
        sha_attr_paths = [path.split('.') for path in self.response_sha_attrs]
        if self.streaming:
            for message in resp:
                self.message_to_git(message, sha_attr_paths)
        else:
            self.message_to_git(resp, sha_attr_paths)

    def message_to_git(self, message, attr_paths):
        for attr_path in attr_paths:
            obj = message
            trav = list(attr_path)
            recurse = False
            while len(trav) > 1:
                attr_name, trav = trav[0], trav[1:]
                recurse = attr_name.endswith('[]')
                if recurse:
                    attr_name = attr_name[:-2]
                obj = getattr(obj, attr_name)
                if recurse:
                    for msg in obj:
                        self.message_to_git(msg, [trav])
                    break

            if recurse:
                # this attr_path was fully treated by recursion
                continue

            obj_attr = trav[0]
            scalar_list = obj_attr.endswith('[]')
            if scalar_list:
                obj_attr = obj_attr[:-2]
            value = getattr(obj, obj_attr)

            if scalar_list:
                for i, sha in enumerate(value):
                    value[i] = self.hg2git(sha)
            else:
                setattr(obj, obj_attr, self.hg2git(value))

    def apply_request_defaults(self, kwargs):
        defaults = self.request_defaults
        if defaults is not None:
            for k, v in defaults.items():
                kwargs.setdefault(k, v)

    def assert_compare(self, **hg_kwargs):
        self.apply_request_defaults(hg_kwargs)

        git_kwargs = self.request_kwargs_to_git(hg_kwargs)

        hg_response = self.rpc('hg', **hg_kwargs)
        git_response = self.rpc('git', **git_kwargs)

        self.response_to_git(hg_response)
        norm = self.normalizer
        if norm is not None:
            norm(self, hg_response, vcs='hg')
            norm(self, git_response, vcs='git')
        assert hg_response == git_response

    def assert_compare_errors(self, same_details=True, **hg_kwargs):
        self.apply_request_defaults(hg_kwargs)

        git_kwargs = self.request_kwargs_to_git(hg_kwargs)
        with pytest.raises(grpc.RpcError) as exc_info_hg:
            self.rpc('hg', **hg_kwargs)
        with pytest.raises(grpc.RpcError) as exc_info_git:
            self.rpc('git', **git_kwargs)
        exc_hg = exc_info_hg.value
        exc_git = exc_info_git.value

        assert exc_hg.code() == exc_git.code()
        if same_details:
            assert exc_hg.details() == exc_git.details()

        return exc_hg, exc_git


def normalize_commit_message(commit):
    """Remove expected differences between commits in Gitaly and HGitaly.

    Some are really testing artifacts, some have eventually to be removed.
    """
    # TODO tree_id should be replaced by HGitaly standard value
    # once HGitaly2 is the norm
    commit.tree_id = ''

    # hg-git may add a branch marker (this is just a test artifact)
    hg_marker = b'\n--HG--\n'
    split = commit.body.split(hg_marker, 1)
    if len(split) > 1:
        commit.body = split[0]
        commit.body_size = commit.body_size - len(split[1]) - len(hg_marker)

    # Either hg-git or Git itself adds a newline if there isn't one.
    # TODO investigate and if it is Git, add the newline in Mercurial
    # response.
    if not commit.body.endswith(b'\n'):
        commit.body = commit.body + b'\n'
        commit.body_size = commit.body_size + 1
