# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Handling of GitLab refs.

This module is primarily geared towards "special" refs, such as
`refs/merge_requests/1/head`, but should really adopt all general
utilities about refs, i.e, anything about a full ref path, such as
`refs/some/thing` and not yet refined to a given type, such as branches
or tags.
"""
from hgext3rd.heptapod import ensure_gitlab_special_refs
from hgext3rd.heptapod import ensure_gitlab_keep_arounds
from hgext3rd.heptapod.special_ref import (
    GITLAB_TYPED_REFS_MISSING,
    parse_special_ref,
    special_refs,
)
from hgext3rd.heptapod.keep_around import iter_keep_arounds


def gitlab_special_ref_target(repo, ref_path):
    """Return the changeset for a special ref.

    :returns: a :class:`changectx` instance, for the unfiltered version of
       ``repo``. The changeset itself may be obsolete.
    """
    name = parse_special_ref(ref_path)
    if name is None:
        return None

    all_special_refs = special_refs(repo)
    if all_special_refs is GITLAB_TYPED_REFS_MISSING:
        # transitional while we still have an inner Git repo
        # would still be the best we can do near the end of HGitaly2 milestone
        all_special_refs = ensure_special_refs(repo)

    sha = all_special_refs.get(name)
    if sha is None:
        return None

    # TODO catch RepoLookupError (case of inconsistency)
    return repo.unfiltered()[sha]


def iter_gitlab_special_refs_as_refs(repo, deref=True):
    """Iterate on special refs, yielding full ref paths and target hashes.
    """
    all_special_refs = special_refs(repo)
    if all_special_refs is GITLAB_TYPED_REFS_MISSING:
        # transitional while we still have an inner Git repo
        # would still be the best we can do near the end of HGitaly2 milestone
        all_special_refs = ensure_special_refs(repo)

    for sref, sha in all_special_refs.items():
        yield b'refs/' + sref, (repo[sha] if deref else sha.decode('ascii'))


def ensure_special_refs(repo):
    return ensure_gitlab_special_refs(repo.ui, repo)


def has_keep_around(repo, sha):
    """Tell if there is a keep around for the given changeset hash.

    :param bytes sha: the changeset hash.
    """
    for ka in iter_keep_arounds(repo):
        if ka is GITLAB_TYPED_REFS_MISSING:
            ensure_gitlab_keep_arounds(repo.ui, repo)
            return has_keep_around(repo, sha)
        if ka == sha:
            return True
    return False


def keep_around_ref_path(sha):
    # TODO should move to py-heptapod
    return b'refs/keep-around/' + sha


def iter_keep_arounds_as_refs(repo, deref=True):
    for sha in iter_keep_arounds(repo):
        if sha is GITLAB_TYPED_REFS_MISSING:
            ensure_gitlab_keep_arounds(repo.ui, repo)
            yield from iter_keep_arounds_as_refs(repo, deref=deref)
            return
        yield (keep_around_ref_path(sha),
               (repo[sha] if deref else sha.decode('ascii')))


def sort_key_ref_changeset_date_asc(ref_chgset):
    """Sorting key function meant for ref items.

    :param ref_chgset: a pair made of ref name and changeset (changectx)
    """
    return ref_chgset[1].date()[0]


def sort_key_ref_changeset_date_desc(ref_chgset):
    """Sorting key function meant for ref items.

    :param ref_chgset: a pair made of ref name and changeset (changectx)
    """
    return -ref_chgset[1].date()[0]
