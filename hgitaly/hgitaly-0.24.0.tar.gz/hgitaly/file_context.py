# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from .git import (
    OBJECT_MODE_EXECUTABLE,
    OBJECT_MODE_LINK,
    OBJECT_MODE_NON_EXECUTABLE,
)


def git_perms(filectx):
    """Return Git representation for file permissions (aka mode).

    Reference: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
    """
    if filectx.islink():
        return OBJECT_MODE_LINK
    elif filectx.isexec():
        return OBJECT_MODE_EXECUTABLE
    else:
        return OBJECT_MODE_NON_EXECUTABLE
