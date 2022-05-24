# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
import shutil

from hgitaly.stub.shared_pb2 import Repository

from heptapod.testhelpers import (
        LocalRepoWrapper,
)
from hgitaly.tests.common import (
    make_empty_repo,
)


@attr.s
class ServiceFixture:
    """Fixture base class to absorb some of the boilerplate.

    See test_ref for example usage.

    There is still a lot of duplication between this class and
    :mod:`hgitaly.tests.common` we should probably merge them together
    at some point.
    """

    stub_cls = attr.ib()
    grpc_channel = attr.ib()
    server_repos_root = attr.ib()
    with_repo = attr.ib(default=True)
    """If ``True``, create a repository in the default storage upon setup.

    The repository details are then accessible in :attr:`grpc_repo`
    and :attr:`repo_wrapper`. If :attr:`with_repo` is ``False``, these
    attributes are initialised to None
    """
    auto_cleanup = attr.ib(default=False)
    """If ``True``, remove repositories tracked by this class upon tear down.

    For other repositories than the one created if :attr:`with_repo` is
    ``True``, this relies on downstream code adding them to
    attr:`repos_to_cleanup`.

    This can be useful for certain services because the
    ``server_repos_root`` fixture has the module scope, but most
    services won't need it because the path of the repository provided by
    this class is unique.
    """

    def __enter__(self):
        self.stub = self.stub_cls(self.grpc_channel)
        if self.with_repo:
            self.repo_wrapper, self.grpc_repo = make_empty_repo(
                self.server_repos_root)
            self.repos_to_cleanup = [self.repo_wrapper.path]
        else:
            self.repo_wrapper = self.grpc_repo = None
            self.repos_to_cleanup = []
        return self

    def __exit__(self, *exc_args):
        if not self.auto_cleanup:
            return

        for repo_path in self.repos_to_cleanup:
            if repo_path.exists():
                shutil.rmtree(repo_path)

    def additional_repo(self, rel_path, storage_name='default'):
        """Register an additional repository by storage relative path.

        The repository is not created (a future option may be introduced
        to do it).

        :returns: repository absolute path and :class:`Repository` instance
          (gRPC message).
        """
        repo_path = self.repo_path(rel_path, storage_name=storage_name)
        repo_msg = Repository(storage_name=storage_name,
                              relative_path=rel_path)
        self.repos_to_cleanup.append(repo_path)
        return repo_path, repo_msg

    def storage_path(self, storage_name='default'):
        """Utility method to avoid depending too much on actual disk layout.

        This repeats the actual implementation just once.
        """
        return self.server_repos_root / storage_name

    def repo_path(self, rel_path, **kw):
        """Utility method to avoid depending too much on actual disk layout.

        This makes no assumption whether the repo nor the storage actually
        exist.
        """
        return self.storage_path(**kw) / rel_path

    def make_repo_wrapper(self, rel_path, **kw):
        """Utility method to avoid depending too much on actual disk layout.

        The repository is expected to exist.
        """
        return LocalRepoWrapper.load(self.repo_path(rel_path, **kw))
