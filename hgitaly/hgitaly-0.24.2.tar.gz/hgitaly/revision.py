# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging
import re

from mercurial import (
    error,
    scmutil,
)
from hgext3rd.heptapod.branch import get_default_gitlab_branch
from hgext3rd.heptapod.keep_around import (
    parse_keep_around_ref,
)
from heptapod.gitlab.branch import (
    gitlab_branch_from_ref,
)
from .branch import (
    gitlab_branch_head
)
from .gitlab_ref import (
    gitlab_special_ref_target
)

logger = logging.getLogger(__name__)

# 40 hex digits for SHA-1, 64 hex digits for SHA-2
_HASH_RX = r'^([0-9A-Fa-f]{40})|([0-9A-Fa-f]{64})$'
CHANGESET_HASH_BYTES_REGEXP = re.compile(_HASH_RX.encode('ascii'))
CHANGESET_HASH_STR_REGEXP = re.compile(_HASH_RX)


class RevisionNotFound(LookupError):
    pass


def gitlab_revision_changeset(repo, revision):
    """Find the changeset for a given GitLab revision.

    In theory, a GitLab revision could be any Git valid revspec, that
    we'd had to translate into its Mercurial counterpart.

    At this point, we support changeset IDs in hex, GitLab branches, tags and
    ``HEAD`` (default GitLab branch).

    Obsolescence
    ------------
    Changeset IDs can return obsolete changesets (this is actually used in
    force push detection, or in Merge Request updates), while symbolic ones
    (branch, tags etc) *should* always return non obsolete changesets.

    :return: the changeset as a :class:`changectx` instance, or ``None``
             if not found.
    """
    if revision == b'HEAD':
        revision = get_default_gitlab_branch(repo)
        if revision is None:
            return None

    ka = parse_keep_around_ref(revision)
    if ka is not None:
        try:
            return repo.unfiltered()[ka]
        except error.RepoLookupError:
            logger.warning("Unresolvable keep-around %r", ka)
            return None

    # non ambigous ref forms: they should obviously take precedence
    # TODO direct reference to tag here as well
    gl_branch = gitlab_branch_from_ref(revision)
    if gl_branch is not None:
        # can return None
        return gitlab_branch_head(repo, gl_branch)

    # special ref
    ctx = gitlab_special_ref_target(repo.unfiltered(), revision)
    if ctx is not None:
        return ctx

    # direct GitLab branch name
    ctx = gitlab_branch_head(repo, revision)
    if ctx is not None:
        return ctx

    try:
        # TODO we should probably give precedence to tags, as Mercurial
        # does, although we should check what Git(aly) really does in
        # case of naming conflicts
        return scmutil.revsingle(repo.unfiltered(), revision)
    except error.RepoLookupError:
        return None  # voluntarily explicit


def gitlab_revision_hash(repo, revision):
    """Return the changeset hexadecimal hash for given GitLab revision

    This is the preferred method to use when handling lists of revisions
    because the contexts retured by func:`gitlab_revision_changeset` may be
    associated to different repository views (filtered or not), hence it
    can be a trap for caller code to use them in revsets.

    Besides the return type, a major difference with
    func:`gitlab_revision_changeset` is that it raises instead of returning
    ``None`` if the revision could not be resolved. This is also more
    handy in loops and comprehensions than checking for or filtering out
    ``None``.

    :returns: the hash, as an hexadecimal bytes string.
    :raises RevisionNotFound:
    """
    ctx = gitlab_revision_changeset(repo, revision)
    if ctx is None:
        raise RevisionNotFound(revision)
    return ctx.hex()
