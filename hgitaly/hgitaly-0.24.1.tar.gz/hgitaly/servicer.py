# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import gc
import logging
import os
import time
import weakref

from grpc import StatusCode
from mercurial import (
    error,
    hg,
    ui as uimod,
)
from mercurial.repoview import _filteredrepotypes
from .stub.shared_pb2 import (
    Repository,
)

GARBAGE_COLLECTING_RATE_GEN2 = 250
GARBAGE_COLLECTING_RATE_GEN1 = 20

logger = logging.getLogger(__name__)


def clear_repo_class(repo_class):
    _filteredrepotypes.pop(repo_class, None)


repos_counter = 0


def gc_collect(generation):
    logger.info("A total of %d repository objects have been "
                "instantiated in this thread since startup. "
                "Garbage collecting (generation %d)",
                repos_counter, generation)
    start = time.time()
    gc_result = gc.collect(generation=generation)
    logger.info("Garbage collection (generation %d) "
                "done in %f seconds "
                "(%d unreachable objects). Current GC stats: %r",
                generation, time.time() - start, gc_result, gc.get_stats())


class HGitalyServicer:
    """Common features of all HGitaly services.

    Attributes:

    - :attr:`storages`: a :class:`dict` mapping storage names to corresponding
      root directory absolute paths, which are given as bytes since we'll have
      to convert paths to bytes anyway, which is the only promise a filesystem
      can make, and what Mercurial expects.
    - :attr:`ui`: base :class:`mercurial.ui.ui` instance from which repository
      uis are derived. In particular, it bears the common configuration.
    """

    def __init__(self, storages):
        self.storages = storages
        self.ui = uimod.ui.load()

    def load_repo(self, repository: Repository, context):
        """Load the repository from storage name and relative path

        :param repository: Repository Gitaly Message, encoding storage name
            and relative path
        :param context: gRPC context (used in error raising)
        :raises: ``KeyError('storage', storage_name)`` if storage is not found.

        Error treatment: the caller doesn't have to do anything specific,
        the status code and the details are already set in context, and these
        are automatically propagated to the client (see corresponding test
        in `test_servicer.py`). Still, the caller can still catch the
        raised exception and change the code and details as they wish.
        """
        global repos_counter
        if repos_counter % GARBAGE_COLLECTING_RATE_GEN2 == 0:
            gc_collect(2)
        elif repos_counter % GARBAGE_COLLECTING_RATE_GEN1 == 0:
            gc_collect(1)

        repos_counter += 1

        # shamelessly taken from heptapod.wsgi for the Hgitaly bootstrap
        # note that Gitaly Repository has more than just a relative path,
        # we'll have to decide what we make of the extra information
        repo_path = self.repo_disk_path(repository, context)
        logger.info("loading repo at %r", repo_path)

        try:
            repo = hg.repository(self.ui, repo_path)
        except error.RepoError as exc:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(repr(exc.args))
            raise KeyError('repo', repo_path)
        weakref.finalize(repo, clear_repo_class, repo.unfiltered().__class__)
        srcrepo = hg.sharedreposource(repo)
        if srcrepo is not None:
            weakref.finalize(srcrepo, clear_repo_class,
                             srcrepo.unfiltered().__class__)

        return repo

    def storage_root_dir(self, storage_name, context):
        """Return the storage directory.

        If the storage is unknown, this sets error code and details
        on the context and raises ``KeyError('storage', storage_name)``
        """
        root_dir = self.storages.get(storage_name)
        if root_dir is None:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details("No storage named %r" % storage_name)
            raise KeyError('storage', storage_name)
        return root_dir

    def repo_disk_path(self, repository: Repository, context):
        rpath = repository.relative_path
        if rpath.endswith('.git'):
            rpath = rpath[:-4] + '.hg'

        root_dir = self.storage_root_dir(repository.storage_name, context)

        # GitLab filesystem paths are always ASCII
        repo_path = os.path.join(root_dir, rpath.encode('ascii'))
        return repo_path

    def temp_dir(self, storage_name, context, ensure=True):
        """Return the path to temporary directory for the given storage

        Similar to what Gitaly uses, with a dedicated path in order
        to be really sure not to overwrite anything. The important feature
        is that the temporary directory is under the root directory of
        the storage, hence on the same file system (atomic renames of
        other files from the storage, etc.)

        :param bool ensure: if ``True``, the temporary directory is created
           if it does not exist yet.
        :raises KeyError: if the storage is unknown
        :raises OSError: if creation fail
        """
        temp_dir = os.path.join(self.storage_root_dir(storage_name, context),
                                b'+hgitaly', b'tmp')
        if not ensure:
            return temp_dir

        # not the proper time to switch everything to pathlib (operates on
        # str paths, but surrogates returned by os.fsdecode() seem to really
        # work well)
        to_create = []
        current = temp_dir
        try:
            while not os.path.exists(current):
                to_create.append(current)
                current = os.path.dirname(current)

            while to_create:
                # same mode as in Gitaly, hence we don't care about groups
                # although this does propagate the setgid bit
                os.mkdir(to_create.pop(), mode=0o755)
        except OSError as exc:
            context.set_code(StatusCode.INTERNAL)
            context.set_details("Error ensuring temporary dir %r: %s" % (
                temp_dir, exc))
            raise

        return temp_dir
