# Copyright 2021-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from mercurial import (
    commands,
    pycompat,
)

GITLAB_PROJECT_FULL_PATH_FILENAME = b'gitlab.project_full_path'


def set_gitlab_project_full_path(repo, full_path: bytes):
    """Store information about the full path of GitLab Project.

    In GitLab terminology, ``full_path`` is the URI path, while ``path``
    its the last segment of ``full_path``.

    In Git repositories, this is stored in config. We could as well use
    the repo-local hgrcs, but it is simpler to use a dedicated file, and
    it makes sense to consider it not part of ``store`` (``svfs``), same
    as ``hgrc``.
    """
    with repo.wlock():
        repo.vfs.write(GITLAB_PROJECT_FULL_PATH_FILENAME, full_path)


def unbundle(repo, bundle_path: str, rails_sync=False):
    """Call unbundle with proper options and conversions.

    :param bool rails_sync: if ``True``, let the synchronization with the
       Rails app proceed (conversion to Git if needed, pre/post-receive hooks,
       etc.)
    """
    # make sure obsmarker creation is allowed while unbundle
    overrides = {(b'experimental', b'evolution'): b'all',
                 }
    if not rails_sync:
        overrides[(b'hooks', b'pretxnclose.heptapod_sync')] = b''

    # TODO it would be nice to have UPSTREAM a method
    # to unbundle from an arbitrary file-like object rather than
    # paths forcing us to dump to disk
    with repo.ui.configoverride(overrides, b'hgitaly.unbundle'):
        commands.unbundle(repo.ui, repo, pycompat.sysbytes(bundle_path))
