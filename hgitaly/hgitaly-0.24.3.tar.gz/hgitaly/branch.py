# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from enum import Enum
from io import BytesIO
import re

from mercurial import (
    error,
    node as nodemod,
    pycompat,
)
from hgext3rd.evolve import headchecking
from heptapod.gitlab.branch import (
    branchmap_branch_from_gitlab_branch,
    gitlab_branch_from_branchmap_branch,
    parse_wild_gitlab_branch,
    gitlab_branch_ref,
)
from hgext3rd.heptapod.branch import (
    GITLAB_BRANCHES_MISSING,
    get_default_gitlab_branch,
    gitlab_branches,
)
from hgext3rd.heptapod import (
    ensure_gitlab_branches as hg_git_ensure_gitlab_branches,
)
from .gitlab_ref import (
    sort_key_ref_changeset_date_asc,
    sort_key_ref_changeset_date_desc,
)


import logging
logger = logging.getLogger(__name__)


class BranchSortBy(Enum):
    """Sort criteria for branches.

    As long as Gitaly does not define a common set of sort criteria
    in `shared.proto`, the enums they use might differ with each request.
    Hence we need to remap to an inner class such as this one.

    Also, we might in the future introduce specific variations, depending on
    conventions for branch representation (which currently give the
    lexicographical ordering putting regular named branches before topics but
    are prone to change)
    """
    FULL_REF_NAME = 0
    UPDATED_ASC = 1
    UPDATED_DESC = 2


def _extract_branchmap_heads(repo, entry,
                             avoid_bookmark_shadowing=False):
    """From the given branchmap entry, extract default head and list of heads.

    The default head is what needs to be returned for a simple branchmap
    branch lookup. It can be ``None`` if all heads are invisible to GitLab
    (closed or bookmarked).

    :param avoid_bookmark_shadowing: if ``True`` the bookmarked revision with
       the highest revno can be returned if there's nothing else
    :return: (default head, all heads visible to GitLab), all given as
             :class:`changectx` instances.
    """
    # branchmap entries results are already sorted by increasing rev number
    revs = [repo[node].rev() for node in entry]
    contexts = (repo[rev]
                for rev in headchecking._filter_obsolete_heads(repo, revs))
    visible = [c for c in contexts if not (c.closesbranch() or c.bookmarks())]

    if not visible and avoid_bookmark_shadowing:
        # rare case, performance is irrelevant, we can re-lookup
        for ctx in (repo[node] for node in reversed(entry)):
            if not ctx.obsolete() and not ctx.closesbranch():
                return ctx, [ctx]

    if not visible:
        return None, visible

    return visible[-1], visible


def changeset_branchmap_entry(repo, ctx):
    """Return the branchmap entry for branch/topic combination of a changeset

    :param ctx: the changeset, given as a :class:`changectx`.
    """
    branch, topic = ctx.branch(), ctx.topic()
    key = branch if not topic else b':'.join((branch, topic))
    return repo.branchmap()[key]


def gitlab_branch_head(repo, gl_branch):
    """Return the unique head of the given GitLab branch.

    Does not resolve other types of "revisions".

    :return: a :class:`changectx` or ``None`` if there's no changeset for
             the given ``gl_branch``.
    """
    gl_branches = gitlab_branches(repo)
    if gl_branches is not GITLAB_BRANCHES_MISSING:
        sha = gl_branches.get(gl_branch)
        if sha is None:
            return None
        return repo[sha]

    logger.warning("gitlab_branch_head for %r: no GitLab branches state file "
                   "defaulting to slow direct analysis.", repo.root)
    wild_hex = parse_wild_gitlab_branch(gl_branch)
    if wild_hex is not None:
        wild_bin = nodemod.bin(wild_hex)
        try:
            wild_ctx = repo[wild_bin]
        except error.RepoLookupError:
            return None

        if wild_ctx.bookmarks():
            # a bookmarked head is never wild
            return None

        heads = _extract_branchmap_heads(
            repo, changeset_branchmap_entry(repo, wild_ctx))[1]
        return wild_ctx if len(heads) > 1 and wild_ctx in heads else None

    branchmap_key = branchmap_branch_from_gitlab_branch(gl_branch)
    if branchmap_key is not None:
        try:
            entry = repo.branchmap()[branchmap_key]
        except KeyError:
            return None
        return _extract_branchmap_heads(
            repo, entry,
            avoid_bookmark_shadowing=(
                gl_branch == get_default_gitlab_branch(repo)),
        )[0]

    # last chance: bookmarks
    bookmark_node = repo._bookmarks.get(gl_branch)
    if bookmark_node is None:
        return None
    return repo[bookmark_node]


def iter_gitlab_branches(repo, deref=True):
    """Iterate on all visible GitLab branches

    Each iteration yields a pair ``(gl_branch, target)`` where ``gl_branch``
    is the name of the GitLab branch and ``target`` is a :class:`changectx`
    instance or a hexadecimal node id, as a :class:`str` instance.

    :param bool deref: if ``True``, resolves targets as :class:`changectx`
      instance, ignoring lookup errors. If ``False``, yield targets as
      hexadecimal node ids.
    """
    gl_branches = gitlab_branches(repo)
    if gl_branches is not GITLAB_BRANCHES_MISSING:
        for branch, sha in gl_branches.items():
            if deref:
                try:
                    yield branch, repo[sha]
                except error.RepoLookupError as exc:
                    logger.error("Unknown changeset ID in GitLab branches "
                                 "statefile for repo at %r: %r",
                                 repo.root, exc)
            else:
                yield branch, sha.decode('ascii')
    else:
        logger.warning("iter_gitlab_branches for %r: "
                       "no GitLab branches state file "
                       "defaulting to slow direct analysis.", repo.root)
        for branch, target in iter_compute_gitlab_branches(repo):
            if not deref:
                target = target.hex().decode('ascii')
            yield branch, target


def gitlab_branches_matcher(patterns):
    """Returns a compiled regexp for pattern matching on GitLab branches

    This is meant to match the reference Go implementation in Gitaly's
    `UpdateRemoteMirror`, which in turn is fed the protected branches pattern.
    Even though we won't implement the same gRPC method (too Git centric), it
    is taken as reference for how glob patterns on branch names are interpreted
    in Gitaly. As of Gitaly 14.4.1::

      // newReferenceMatcher returns a regexp which matches references that should
      // be updated in the mirror repository. Tags are always matched successfully.
      // branchMatchers optionally contain patterns that are used to match branches.
      // The patterns should only include the branch name without the `refs/heads/`
      // prefix. "*" can be used as a wilcard in the patterns. If no branchMatchers
      // are specified, all branches are matched successfully.
      func newReferenceMatcher(branchMatchers [][]byte) (*regexp.Regexp, error) {
          sb := &strings.Builder{}
          sb.WriteString("^refs/tags/.+$|^refs/heads/(")

          for i, expression := range branchMatchers {
              segments := strings.Split(string(expression), "*")
              for i := range segments {
                  segments[i] = regexp.QuoteMeta(segments[i])
              }

              sb.WriteString(strings.Join(segments, ".*"))

              if i < len(branchMatchers)-1 {
                  sb.WriteString("|")
              }
          }

          if len(branchMatchers) == 0 {
              sb.WriteString(".+")
          }

          sb.WriteString(")$")

          return regexp.Compile(sb.String())
      }

    Difference in our implementation:

    - the returned pattern will be made to match branch
      names directly instead of refs. We don't have to take care of tags.
    - we return ``None`` if ``patterns`` is empty
    """  # noqa: E501  (long quote from Golang code)
    pattern_seen = False

    re_pattern = BytesIO()
    re_pattern.write(b'^')
    for pattern in patterns:
        if pattern_seen:
            re_pattern.write(b'|')
        pattern_seen = True
        re_pattern.write(b'(')
        re_pattern.write(b'.*'.join(
            re.escape(segment) for segment in pattern.split(b'*')))
        re_pattern.write(b')')

    if pattern_seen:
        re_pattern.write(b'$')
    return re.compile(re_pattern.getvalue())


def iter_gitlab_branches_matching(repo, patterns):
    rx = gitlab_branches_matcher(patterns)
    # OPTIM this has the drawback of resolving the changeset contexts
    # for branches that don't match. Not expected to be a performance
    # problem at this stage, but can be further optimized by performing
    # the pattern matching in `iter_gitlab_branches()`
    return ((name, ctx) for name, ctx in iter_gitlab_branches(repo)
            if rx.match(name) is not None)


def iter_compute_gitlab_branches(repo):
    """Generator that computes GitLab branches from scratch"""
    for key, entry in pycompat.iteritems(repo.branchmap()):
        gl_branch = gitlab_branch_from_branchmap_branch(key)
        default, visible = _extract_branchmap_heads(
            repo, entry,
            avoid_bookmark_shadowing=(
                gl_branch == get_default_gitlab_branch(repo)))
        if not visible:
            continue

        yield gl_branch, default
        if len(visible) > 1:
            for head in visible:
                yield b'wild/' + head.hex(), head

    for key, node in pycompat.iteritems(repo._bookmarks):
        yield key, repo[node]


def iter_gitlab_branches_as_refs(repo, **kwargs):
    """Same as :func:`iter_gitlab_branches`, yielding full Git ref paths.
    """
    for branch, target in iter_gitlab_branches(repo, **kwargs):
        yield gitlab_branch_ref(branch), target


def sorted_gitlab_branches_as_refs(repo, after=None, sort_by=None, deref=True):
    """Return all visible, GitLab branches, sorted.

    :param bytes after: full ref name of a branch. If not `None`,
       return only branches which occur strictly after the given one in the
       sort ordering used.
    :param bool deref: same as in :func:`iter_gitlab_branches`, except
       that dereferencing may happen internally if the sort criterion
       requires it.
    :params kwargs: passed over to :func:`iter_gitlab_branches`
    :returns: iterable of pairs (full Git ref name, changectx or str).
      Can be just an iterator.

    By default GitLab sorts branches lexicographically.
    Since Heptapod is using `/` separated special names,
    it would make sense to perform a variation over that
    (named branches first, then topics, lexicographically sorted
    for each, of course).
    """
    # TODO OPTIM (would be premature until we have some profile figures
    # pointing at this function)
    # Depending on the total size of ref_chgsets, it might be better to
    # - do any linear filtering before sorting
    # - resolve changecontexts only while yielding, a bigger refactoring
    #   also involving `iter_gitlab_branches()`.
    if sort_by == BranchSortBy.FULL_REF_NAME:
        sort_key = None
    elif sort_by == BranchSortBy.UPDATED_ASC:
        sort_key = sort_key_ref_changeset_date_asc
    elif sort_by == BranchSortBy.UPDATED_DESC:
        sort_key = sort_key_ref_changeset_date_desc

    inner_deref = deref if sort_by == BranchSortBy.FULL_REF_NAME else True

    ref_targets = sorted(iter_gitlab_branches_as_refs(repo, deref=inner_deref),
                         key=sort_key)
    if after is not None:
        ref_targets = iter(ref_targets)
        for ref, _ in ref_targets:
            if ref == after:
                break

    if inner_deref and not deref:
        ref_targets = ((ref, target.hex().decode('ascii'))
                       for ref, target in ref_targets)
    yield from ref_targets


def ensure_gitlab_branches_state_file(repo):
    """Make sure that the GitLab branches state file exists.

    Some implementations have to rely on it, and we will soon basically
    require in in practice, lest the performance degradation become
    intolerable.

    For now, we can assume that all repositories are actually handled with
    the mirroring to Git code from hgext3rd.heptapod.

    When that becomes false, we'll be faced with two options:

    - have enough trust in our migration scenarios that we simply make it
      a hard requirement or
    - keep the code able to recompute all GitLab branches around, such as
      :func:`gitlab_branch_head` as of this writing and use it to reconstruct
      the file.

    See also py-heptapod#8
    """
    hg_git_ensure_gitlab_branches(repo.ui, repo)
