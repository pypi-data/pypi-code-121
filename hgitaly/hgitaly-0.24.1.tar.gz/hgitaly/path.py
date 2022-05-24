# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import (
    error,
    pathutil,
)


class InvalidPath(ValueError):
    pass


def validate_relative_path(repo, path):
    """Equivalent of `storage.ValidateRelativePath` in Gitaly Golang code.

    Quoting the doc-comment:

      ValidateRelativePath validates a relative path by joining it with rootDir
      and verifying the result is either rootDir or a path within rootDir.
      Returns clean relative path from rootDir to relativePath
      or an ErrRelativePathEscapesRoot if the resulting path is not contained
      within rootDir.

    """
    auditor = pathutil.pathauditor(repo.root, realfs=False)
    try:
        return pathutil.canonpath(repo.root, repo.root, path, auditor)
    except error.Abort:
        raise InvalidPath(path)
