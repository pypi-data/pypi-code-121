# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

from heptapod.gitlab.branch import (
    gitlab_branch_from_ref,
    gitlab_branch_ref,
)
from hgext3rd.heptapod.branch import get_default_gitlab_branch
from hgext3rd.heptapod.typed_ref import GITLAB_TYPED_REFS_MISSING
from hgext3rd.heptapod.special_ref import (
    parse_special_ref,
    special_refs,
    write_special_refs,
)
from hgext3rd.heptapod.keep_around import (
    parse_keep_around_ref,
)

from ..errors import (
    internal_error,
    invalid_argument,
    not_found,
    not_implemented,
)
from ..pagination import (
    extract_limit,
)
from ..stub.shared_pb2 import (
    Branch,
    GitCommit,
    SortDirection,
)
from ..stub.ref_pb2 import (
    FindDefaultBranchNameRequest,
    FindDefaultBranchNameResponse,
    FindAllBranchNamesRequest,
    FindAllBranchNamesResponse,
    FindAllTagNamesRequest,
    FindAllTagNamesResponse,
    FindLocalBranchesRequest,
    FindLocalBranchCommitAuthor,
    FindLocalBranchResponse,
    FindLocalBranchesResponse,
    FindAllBranchesRequest,
    FindAllBranchesResponse,
    FindAllTagsRequest,
    FindAllTagsResponse,
    FindTagRequest,
    FindTagResponse,
    FindAllRemoteBranchesRequest,
    FindAllRemoteBranchesResponse,
    RefExistsRequest,
    RefExistsResponse,
    FindBranchRequest,
    FindBranchResponse,
    DeleteRefsRequest,
    DeleteRefsResponse,
    ListBranchNamesContainingCommitRequest,
    ListBranchNamesContainingCommitResponse,
    ListTagNamesContainingCommitRequest,
    ListTagNamesContainingCommitResponse,
    GetTagSignaturesRequest,
    GetTagSignaturesResponse,
    GetTagMessagesRequest,
    GetTagMessagesResponse,
    PackRefsRequest,
    PackRefsResponse,
    ListRefsRequest,
    ListRefsResponse,
    FindRefsByOIDRequest,
    FindRefsByOIDResponse,
)
from ..stub.ref_pb2_grpc import RefServiceServicer

from ..branch import (
    BranchSortBy,
    gitlab_branch_head,
    iter_gitlab_branches,
    iter_gitlab_branches_as_refs,
    sorted_gitlab_branches_as_refs,
)
from ..gitlab_ref import (
    ensure_special_refs,
    has_keep_around,
    iter_gitlab_special_refs_as_refs,
    iter_keep_arounds_as_refs,
)
from ..tag import (
    EXCLUDED_TAG_TYPES,
    iter_gitlab_tags,
    iter_gitlab_tags_as_refs,
)
from .. import message
from ..servicer import HGitalyServicer
from ..util import chunked

logger = logging.getLogger(__name__)
DEFAULT_BRANCH_FILE_NAME = b'default_gitlab_branch'
FIND_LOCAL_BRANCHES_SORT_BY_TO_INNER = {
    FindLocalBranchesRequest.SortBy.NAME: BranchSortBy.FULL_REF_NAME,
    FindLocalBranchesRequest.SortBy.UPDATED_ASC: BranchSortBy.UPDATED_ASC,
    FindLocalBranchesRequest.SortBy.UPDATED_DESC: BranchSortBy.UPDATED_DESC
}


class RefServicer(RefServiceServicer, HGitalyServicer):
    """RefService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def FindDefaultBranchName(
            self,
            request: FindDefaultBranchNameRequest,
            context) -> FindDefaultBranchNameResponse:
        logger.debug("Processing %r", message.Logging(request))
        try:
            repo = self.load_repo(request.repository, context)
        except KeyError as exc:
            return not_found(context, FindDefaultBranchNameResponse,
                             "repository not found: " + repr(exc.args))
        branch = get_default_gitlab_branch(repo)
        if branch is None:
            # Very coincidental, but this ends up as empty GitLab branch name
            # which the chain of || in app/models/concerns/repository
            # that eventually turns this in `nil`, which is the marker
            # used in the hg_fixup_default_branch in PostReceive…
            # TODO now that we have richer notifications, make a clear one
            # for that case
            branch = b''
            logger.warning("FindDefaultBranchName: no information stored "
                           "for repo at %r, returning harcoded default %r",
                           repo, branch)

        return FindDefaultBranchNameResponse(name=gitlab_branch_ref(branch))

    def FindAllBranchNames(self,
                           request: FindAllBranchNamesRequest,
                           context) -> FindAllBranchNamesResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        for chunk in chunked(iter_gitlab_branches_as_refs(repo)):
            yield FindAllBranchNamesResponse(names=(br[0] for br in chunk))

    def FindAllTagNames(self,
                        request: FindAllTagNamesRequest,
                        context) -> FindAllTagNamesResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        # TODO SPEC it's not clear whether GitLab actually expect the
        # tags to be in any ordering. At a quick glance it doesn't, but
        # maye we'll end up with confused users because it'd make no sense
        # in the UI.
        for chunk in chunked(iter_gitlab_tags_as_refs(repo)):
            yield FindAllTagNamesResponse(names=(nc[0] for nc in chunk))

    def FindLocalBranches(self,
                          request: FindLocalBranchesRequest,
                          context) -> FindLocalBranchesResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        limit = extract_limit(request)
        if limit == 0:
            # util.chunk consider this means no limit,
            # shared.proto defines it to mean an empty response
            return

        after = request.pagination_params.page_token
        # TODO encoding?
        after = after.encode('utf-8') if after else None
        sort_by = FIND_LOCAL_BRANCHES_SORT_BY_TO_INNER.get(request.sort_by)
        for chunk in chunked(sorted_gitlab_branches_as_refs(repo,
                                                            sort_by=sort_by,
                                                            after=after),
                             limit=limit):
            yield FindLocalBranchesResponse(
                branches=(find_local_branch_response(name, head)
                          for name, head in chunk),
            )

    def FindAllBranches(self,
                        request: FindAllBranchesRequest,
                        context) -> FindAllBranchesResponse:
        logger.debug("Processing %r", message.Logging(request))
        Branch = FindAllBranchesResponse.Branch
        repo = self.load_repo(request.repository, context)
        for chunk in chunked(iter_gitlab_branches(repo)):
            yield FindAllBranchesResponse(
                branches=(Branch(name=name, target=message.commit(head))
                          for name, head in chunk))

    def FindAllTags(self,
                    request: FindAllTagsRequest,
                    context) -> FindAllTagsResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        for chunk in chunked(iter_gitlab_tags(repo)):
            yield FindAllTagsResponse(tags=[message.tag(name, ctx)
                                            for name, ctx in chunk])

    def FindTag(self,
                request: FindTagRequest,
                context) -> FindTagResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        name = request.tag_name
        if repo.tagtype(name) in EXCLUDED_TAG_TYPES:
            # tagtype() returns None if the tag does not exist at all.
            # Yes, Gitaly returns INTERNAL error (see Gitaly Comparison test)
            return internal_error(context, FindTagResponse,
                                  message=b'no tag found')

        node = repo.tags()[name]
        return FindTagResponse(tag=message.tag(name, repo[node]))

    def FindAllRemoteBranches(self,
                              request: FindAllRemoteBranchesRequest,
                              context) -> FindAllRemoteBranchesResponse:
        """There is no concept of "remote branch" in Mercurial."""
        logger.debug("Processing %r", message.Logging(request))
        return iter(())

    def RefExists(self,
                  request: RefExistsRequest,
                  context) -> RefExistsResponse:
        logger.debug("Processing %r", message.Logging(request))
        ref = request.ref
        if not ref.startswith(b'refs/'):
            # TODO SPEC commment in ref.proto says `ref` must start with
            # refs/ but doesn't say if False should be returned or an error
            # be set.
            return RefExistsResponse(value=False)

        # TODO protect here
        repo = self.load_repo(request.repository, context)

        gl_branch = gitlab_branch_from_ref(ref)
        if gl_branch is not None:
            return RefExistsResponse(
                value=gitlab_branch_head(repo, gl_branch) is not None)

        gl_tag = gitlab_tag_from_ref(ref)
        if gl_tag is not None:
            return RefExistsResponse(
                value=repo.tagtype(gl_tag) not in EXCLUDED_TAG_TYPES)

        special = parse_special_ref(ref)
        if special is not None:
            srefs = special_refs(repo)
            if srefs is GITLAB_TYPED_REFS_MISSING:
                srefs = ensure_special_refs(repo)

            return RefExistsResponse(value=special in srefs)

        keep_around = parse_keep_around_ref(ref)
        if keep_around is not None:
            return RefExistsResponse(value=has_keep_around(repo, keep_around))
        return RefExistsResponse(value=False)

    def FindBranch(self,
                   request: FindBranchRequest,
                   context) -> FindBranchResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        name = request.name
        if name.startswith(b'refs/'):
            name = gitlab_branch_from_ref(request.name)

        if name is None:
            # TODO SPEC check if we really must exclude other refs
            return FindBranchResponse(branch=None)

        head = gitlab_branch_head(repo, name)
        if head is None:
            return FindBranchResponse(branch=None)

        return FindBranchResponse(
            branch=Branch(name=name, target_commit=message.commit(head)))

    def DeleteRefs(self,
                   request: DeleteRefsRequest,
                   context) -> DeleteRefsResponse:
        logger.debug("Processing %r", message.Logging(request))
        except_prefix = request.except_with_prefix
        refs = request.refs
        if refs and except_prefix:
            return invalid_argument(
                context, DeleteRefsResponse,
                "DeleteRefs: ExceptWithPrefix and Refs are mutually exclusive")

        repo = self.load_repo(request.repository, context)
        srefs = special_refs(repo)
        if srefs is GITLAB_TYPED_REFS_MISSING:
            srefs = ensure_special_refs(repo)
        if refs:
            # Using copy() to avoid doing anything (natural rollback) if
            # one of the ref is bogus.
            # It's not really important right now because we have
            # no cache of loaded repos, but that will change sooner or later.
            srefs = srefs.copy()
            err = remove_special_refs(srefs, refs)
            if err is not None:
                return DeleteRefsResponse(git_error=err)

        if except_prefix:
            srefs = special_refs_matching_prefixes(srefs, except_prefix)

        write_special_refs(repo, srefs)
        return DeleteRefsResponse()

    def ListBranchNamesContainingCommit(
            self,
            request: ListBranchNamesContainingCommitRequest,
            context) -> ListBranchNamesContainingCommitResponse:
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)

        gl_branches_by_heads = {}
        for gl_branch, head in iter_gitlab_branches(repo):
            rev = head.rev()
            gl_branches_by_heads.setdefault(rev, []).append(gl_branch)

        heads = repo.revs(b'%ld and %s::', gl_branches_by_heads,
                          request.commit_id)
        # TODO SPEC since there's a limit, we'll have to know what is
        # the expected ordering.
        #
        # In Gitaly sources, this is in refnames.go, which in turns call
        # `git for-each-ref` without a `sort` option. Then according to
        # the man page:
        #  --sort=<key>
        #      A field name to sort on. Prefix - to sort in descending order
        #      of the value. When unspecified, refname is used.
        for chunk in chunked((gl_branch
                              for head in heads
                              for gl_branch in gl_branches_by_heads[head]),
                             limit=request.limit):
            yield ListBranchNamesContainingCommitResponse(
                branch_names=chunk)

    def ListTagNamesContainingCommit(
            self,
            request: ListTagNamesContainingCommitRequest,
            context) -> ListTagNamesContainingCommitResponse:
        logger.debug("Processing %r", message.Logging(request))
        # TODO support ordering, see similar method for branches
        repo = self.load_repo(request.repository, context)
        revs = repo.revs("%s:: and tag()", request.commit_id)
        tag_names = (name for rev in revs for name in repo[rev].tags()
                     if repo.tagtype(name) not in EXCLUDED_TAG_TYPES)
        for chunk in chunked(tag_names, limit=request.limit):
            yield ListTagNamesContainingCommitResponse(tag_names=chunk)

    def GetTagSignatures(self,
                         request: GetTagSignaturesRequest,
                         context) -> GetTagSignaturesResponse:
        return not_implemented(context, GetTagSignaturesResponse,
                               issue=75)  # pragma no cover

    def GetTagMessages(self,
                       request: GetTagMessagesRequest,
                       context) -> GetTagMessagesResponse:
        """Return messages of the given tags.

        In Mercurial, all tags have messages, and these are descriptions
        of the changests that give them values.

        For now, we'll consider that the id of a tag is the nod id of the
        changeset that gives it its current value.
        """
        logger.debug("Processing %r", message.Logging(request))
        repo = self.load_repo(request.repository, context)
        # TODO check that the given id is indeed for a tag, i.e. a
        # changeset that affects .hgtags?
        for tag_id in request.tag_ids:
            yield GetTagMessagesResponse(tag_id=tag_id,
                                         message=repo[tag_id].description())

    def ListNewCommits(self, request, context):
        """Not relevant for Mercurial

        From ``ref.proto``:
            Returns commits that are only reachable from the ref passed

        But actually, the request has a ``commit_id`` field, and it's not
        ``bytes``, hence can't be used for a ref.

        The reference Gitaly implementation is in `list_new_commits.go`.
        It boils down to::

          git rev-list --not --all ^oid

        with ``oid`` being ``request.commit id`` (not really a ref, then).
        additional comment: "the added ^ is to negate the oid since there is
        a --not option that comes earlier in the arg list"

        Note that ``--all`` includes Git refs that are descendents of the
        given commit. In other words, the results are ancestors of the
        given commit that would be garbage collected unless they get a ref
        soon.

        In the whole of the GitLab FOSS code base (as of GitLab 12.10),
        this is used only in pre-receive changes checks, i.e, before any ref
        has been assigned to commits that are new, indeed.

        We'll need a Mercurial specific version of the pre-receive check
        anyway.

        With HGitaly, all Mercurial changesets are at least ancestors of
        a GitLab branch head, the only exception not being closed heads,
        which are not mapped, so the results should boil down to something like
        ``reverse(::x and ::(heads() and closed()))``
        """
        raise NotImplementedError(
            "Not relevant for Mercurial")  # pragma: no cover

    def ListNewBlobs(self, request, context):
        """Not relevant for Mercurial.

        This is the same as :meth:`ListNewCommits()`, returning the blobs.
        In Gitaly sources, this is done by adding ``--objects`` to the
        otherwise same call to ``git rev-list`` as for :meth:`ListNewCommits`.

        As of GitLab 12.10, this is used only in
        ``GitAccess#check_changes_size`` (enforcing size limits for pushes).
        """
        raise NotImplementedError(
            "Not relevant for Mercurial")  # pragma: no cover

    def PackRefs(self, request: PackRefsRequest, context) -> PackRefsResponse:
        """Not relevant for Mercurial, does nothing.
        """
        # repr(Repository) contains newlines
        logger.warning("Ignored irrelevant PackRefs request %r",
                       message.Logging(request))
        return PackRefsResponse()

    def ListRefs(self, request: ListRefsRequest,
                 context) -> ListRefsResponse:
        # The only options actually in use as of GitLab 14.8
        # are head=true and default sort (client is `gitaly-backup`).
        if (request.sort_by.key != ListRefsRequest.SortBy.Key.REFNAME
                or request.sort_by.direction != SortDirection.ASCENDING):
            return not_implemented(context, ListRefsResponse,
                                   issue=97)  # pragma no cover

        Reference = ListRefsResponse.Reference
        repo = self.load_repo(request.repository, context)

        refs = list(iter_gitlab_branches_as_refs(repo, deref=False))
        if request.head:
            branch = get_default_gitlab_branch(repo)
            if branch is not None:
                head = gitlab_branch_head(repo, branch)
                if head is not None:
                    refs.append((b'HEAD', head.hex().decode('ascii')))
        refs.extend(iter_gitlab_tags_as_refs(repo, deref=False))
        refs.extend(iter_gitlab_special_refs_as_refs(repo, deref=False))
        refs.extend(iter_keep_arounds_as_refs(repo, deref=False))

        if not refs:
            # avoid yielding an empty response, as Gitaly does not.
            # TODO consider doing that in the `chunked()` helper,
            # this looks to be rather systematic.
            return

        refs.sort()

        for chunk in chunked(refs):
            yield ListRefsResponse(
                references=(Reference(name=name, target=target)
                            for name, target in chunk))

    def FindRefsByOID(self, request: FindRefsByOIDRequest,
                      context) -> FindRefsByOIDResponse:
        return not_implemented(context, FindRefsByOIDResponse,
                               issue=89)  # pragma no cover


def flbr_author(commit: GitCommit):
    """Extract commit intro specific fields of FindLocalBranchCommitAuthor."""
    return FindLocalBranchCommitAuthor(
        name=commit.name,
        email=commit.email,
        date=commit.date,
        timezone=commit.timezone,
    )


def find_local_branch_response(name, head):
    commit = message.commit(head)
    return FindLocalBranchResponse(
        name=name,
        commit_id=commit.id,
        commit_subject=commit.subject,
        commit_author=flbr_author(commit.author),
        commit_committer=flbr_author(commit.committer),
        commit=commit,
    )


TAG_REF_PREFIX = b'refs/tags/'


def gitlab_tag_from_ref(ref):
    if ref.startswith(TAG_REF_PREFIX):
        return ref[len(TAG_REF_PREFIX):]


def remove_special_refs(special_refs, to_remove):
    """Remove given elements of the ``special_refs`` mapping.

    :param dict special_refs: the special refs to remove from, whose keys
       are the shortened special ref name.
    :param to_remove: iterable of full ref names to remove.
    :returns: ``None`` if ok, else an error message.

    It is not an error to remove an absent ref, but it is one to request
    removal of a ref that is not a special ref.
    """
    for ref in to_remove:
        name = parse_special_ref(ref)
        if name is None:
            return (
                "Only special refs, such as merge-requests (but "
                "not keep-arounds) can be directly deleted in Mercurial, "
                "got %r" % ref)
        special_refs.pop(name, None)


def special_refs_matching_prefixes(special_refs, prefixes):
    """Return a sub-mapping of special refs matching given prefixes

    :param prefixes: given as full ref names, e.g. `refs/pipelines`.
        Any such prefix that would not be a special ref is simply ignored.
    """
    # Don't use parse_special_ref here, even if tempting: it would
    # not accept prefixes without trailing slashes, such as `refs/pipelines`
    # nor more partial prefixes, such as `refs/pipe`. Currently all used
    # prefixes are full with trailing slash, but if upstream developers
    # ever use a more partial prefix, this would result in data loss
    short_prefixes = {pref[5:] for pref in prefixes
                      if pref.startswith(b'refs/')}

    return {name: target for name, target in special_refs.items()
            if any(name.startswith(prefix) for prefix in short_prefixes)}
