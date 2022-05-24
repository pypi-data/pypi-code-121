# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from io import BytesIO
import attr

from ..errors import (
    not_found,
    unknown_error,
    unavailable_error,
)
from ..oid import (
    blob_oid,
)
from ..git import (
    NULL_BLOB_OID,
    EMPTY_TREE_OID,
)
from mercurial import (
    copies,
    node,
    patch as patchmod,
    pycompat,
    diffutil,
    cmdutil,
    scmutil,
)
from ..stub.diff_pb2 import (
    ChangedPaths,
    CommitDiffRequest,
    CommitDiffResponse,
    CommitDelta as MsgCommitDelta,
    CommitDeltaRequest,
    CommitDeltaResponse,
    DiffStats as MsgDiffStats,
    FindChangedPathsRequest,
    FindChangedPathsResponse,
    RawDiffRequest,
    RawDiffResponse,
    RawPatchRequest,
    RawPatchResponse,
    DiffStatsRequest,
    DiffStatsResponse,
)
from ..stub.diff_pb2_grpc import DiffServiceServicer

from ..servicer import HGitalyServicer
from ..revision import gitlab_revision_changeset
from ..stream import (
    aggregate_flush_batch,
    concat_resplit,
    iter_boolean_lookahead,
    split_batches,
    WRITE_BUFFER_SIZE,
)
from ..util import chunked


logger = logging.getLogger(__name__)
# Copied from mercurial/patch.py
# TODO even though, this is bytes and not octal, would be better
# to use the constants in `hgitaly.git`
gitmode = {b'l': b'120000', b'x': b'100755', b'': b'100644'}
nullid = node.nullid
nullhex = node.nullhex
nullrev = node.nullrev
hex = node.hex

DIFF_MSG_SIZE_THRESHOLD = 5 * 1024
"""DIFF_MSG_SIZE_THRESHOLD controls the max size of response.raw_patch_data
As per Gitaly, this threshold is used only by CommitDiff and CommitDelta
"""

MAX_NUM_STAT_BATCH_SIZE = 1000
"""MAX_NUM_STAT_BATCH_SIZE limits the number of stats in a batch
"""
MAX_FILES_UPPERBOUND = 5000
"""MAX_FILES_UPPERBOUND controls how much max_files limit can reach"""
MAX_LINES_UPPERBOUND = 250000
"""MAX_LINES_UPPERBOUND controls how much max_lines limit can reach"""
MAX_BYTES_UPPERBOUND = 5000 * 5120  # 24MB
"""MAX_BYTES_UPPERBOUND controls how much max_bytes limit can reach"""
SAFE_MAX_FILES_UPPERBOUND = 500
"""SAFE_MAX_FILES_UPPERBOUND controls how much safe_max_files limit can reach
"""
SAFE_MAX_LINES_UPPERBOUND = 25000
"""SAFE_MAX_LINES_UPPERBOUND controls how much safe_max_lines limit can reach
"""
SAFE_MAX_BYTES_UPPERBOUND = 500 * 5120  # 2.4MB
"""SAFE_MAX_BYTES_UPPERBOUND controls how much safe_max_bytes limit can reach
"""
MAX_PATCH_BYTES_UPPERBOUND = 512000  # 500KB
"""MAX_PATCH_BYTES_UPPERBOUND controls how much max_patch_bytes limit can reach
"""

Status_Type_Map = dict(
    added=ChangedPaths.Status.ADDED,
    modified=ChangedPaths.Status.MODIFIED,
    removed=ChangedPaths.Status.DELETED,
    copied=ChangedPaths.Status.COPIED,
    # Note: Mercurial includes TYPE_CHANGE
    # (symlink, regular file, submodule...etc) in MODIFIED status
)


@attr.s
class Limits:
    # If true, max{_files,_lines,_bytes} will cause parsing to stop if any of
    # these limits is reached
    enforce_limits = attr.ib(False)
    # Number of maximum files to parse. The file parsed after this limit is
    # reached is marked as the overflow.
    max_files = attr.ib(0)
    # Number of diff lines to parse (including lines preceded with --- or +++).
    # The file in which limit is reached is discarded and marked as overflow.
    max_lines = attr.ib(0)
    # Number of bytes to parse (including lines preceded with --- or +++).
    # The file in which limit is reached is discarded and marked as overflow.
    max_bytes = attr.ib(0)
    # Number of bytes a single patch can have. Patches surpassing this limit
    # are pruned / nullified.
    max_patch_bytes = attr.ib(0)
    # If true, safe_max{_files,_lines,_bytes} will cause diffs to collapse
    # (i.e. patches are emptied) after any of these limits reached
    collapse_diffs = attr.ib(False)
    # Number of files to parse, after which all subsequent files are collapsed.
    safe_max_files = attr.ib(0)
    # Number of lines to parse (including lines preceded with --- or +++),
    # after which all subsequent files are collapsed.
    safe_max_lines = attr.ib(0)
    # Number of bytes to parse (including lines preceded with --- or +++),
    # after which all subsequent files are collapsed.
    safe_max_bytes = attr.ib(0)


# _enforce_limits_upperbound ensures every limit value is within its
# corresponding upperbound
def _enforce_limits_upperbound(lim):
    lim.max_files = min(lim.max_files, MAX_FILES_UPPERBOUND)
    lim.max_lines = min(lim.max_lines, MAX_LINES_UPPERBOUND)
    lim.max_bytes = min(lim.max_bytes, MAX_BYTES_UPPERBOUND)
    lim.safe_max_files = min(lim.safe_max_files, SAFE_MAX_FILES_UPPERBOUND)
    lim.safe_max_lines = min(lim.safe_max_lines, SAFE_MAX_LINES_UPPERBOUND)
    lim.safe_max_bytes = min(lim.safe_max_bytes, SAFE_MAX_BYTES_UPPERBOUND)
    lim.max_patch_bytes = min(lim.max_patch_bytes, MAX_PATCH_BYTES_UPPERBOUND)


@attr.s
class CurrDiff:
    bytes_count = attr.ib(0)
    collapsed = attr.ib(False)
    line_count = attr.ib(0)
    patch = attr.ib(BytesIO())
    too_large = attr.ib(False)


@attr.s
class Parser:
    """Parser holds necessary state for parsing a diff stream"""
    limits = attr.ib()
    curr_diff = attr.ib()
    files_processed = attr.ib(0)
    lines_processed = attr.ib(0)
    bytes_processed = attr.ib(0)
    finished = attr.ib(False)
    overflow_marker = attr.ib(False)

    # In principle, "exceeded" should be > and not >=, but that's what Gitaly's
    # Golang implementation does. Looks like only `safe_max_lines_exceeded`
    # truly respecting this, for now.
    def max_files_exceeded(self):
        return self.files_processed >= self.limits.max_files

    def safe_max_files_exceeded(self):
        return self.files_processed >= self.limits.safe_max_files

    def max_bytes_exceeded(self):
        total_bytes = self.bytes_processed + self.curr_diff.bytes_count
        return total_bytes >= self.limits.max_bytes

    def safe_max_bytes_exceeded(self):
        total_bytes = self.bytes_processed + self.curr_diff.bytes_count
        return total_bytes > self.limits.safe_max_bytes

    def max_lines_exceeded(self):
        total_lines = self.lines_processed + self.curr_diff.line_count
        return total_lines >= self.limits.max_lines

    def safe_max_lines_exceeded(self):
        total_lines = self.lines_processed + self.curr_diff.line_count
        return total_lines > self.limits.safe_max_lines

    def is_over_limits(self):
        return (
            self.max_files_exceeded()
            or self.max_bytes_exceeded()
            or self.max_lines_exceeded()
        )

    def is_over_safe_limits(self):
        return (
            self.safe_max_files_exceeded()
            or self.safe_max_bytes_exceeded()
            or self.safe_max_lines_exceeded()
        )

    def parse(self, iter_file_hunks):
        # For explicitness, let's instantiate a new BytesIO obj for each file
        self.curr_diff.patch = BytesIO()
        for diffhunk in iter_file_hunks:
            self.curr_diff.patch.write(diffhunk)
            if diffhunk.startswith(b'@@'):
                diffhunk = diffhunk.split(b'\n', 1)[-1]
            lines = diffhunk.splitlines(True)
            self.curr_diff.bytes_count += len(diffhunk)
            self.curr_diff.line_count += len(lines)

        if self.limits.collapse_diffs:
            if self.is_over_safe_limits():
                self.curr_diff.patch = BytesIO()
                self.curr_diff.collapsed = True

        if self.limits.enforce_limits:
            # Apply single-file size limit
            # Note: here we are not comparing with curr_diff.bytes_count
            curr_patch = self.curr_diff.patch.getvalue()
            if len(curr_patch) >= self.limits.max_patch_bytes:
                self.curr_diff.patch = BytesIO()
                self.curr_diff.too_large = True

            if self.is_over_limits():
                self.finished = True
                self.overflow_marker = True

    def consume_curr_diff(self):
        self.files_processed += 1
        self.bytes_processed += self.curr_diff.bytes_count
        self.lines_processed += self.curr_diff.line_count
        self.curr_diff = CurrDiff()


def get_commitDiff_parser(request):
    limits = Limits()
    if request.enforce_limits:
        limits.enforce_limits = True
        limits.max_files = request.max_files
        limits.max_lines = request.max_lines
        limits.max_bytes = request.max_bytes
        limits.max_patch_bytes = request.max_patch_bytes
    if request.collapse_diffs:
        limits.collapse_diffs = True
        limits.safe_max_files = request.safe_max_files
        limits.safe_max_lines = request.safe_max_lines
        limits.safe_max_bytes = request.safe_max_bytes
    _enforce_limits_upperbound(limits)
    return Parser(limits, CurrDiff())


class DiffServicer(DiffServiceServicer, HGitalyServicer):
    """DiffService implementation.

    Note: There is a case where we can have differences in HGitaly's and
    Gitaly's DiffService responses. This happens with the renames when the
    similarity index is less than 50% in that case Git doesn't consider it
    a 'rename' but Hg does (as Hg has explicit tracking of copies and renames).
    """
    def CommitDiff(self, request: CommitDiffRequest,
                   context) -> CommitDiffResponse:
        parsed_request = parse_diff_request(self, request, context)
        parsed, repo, ctx_from, ctx_to = parsed_request
        if not parsed:
            return unavailable_error(context, CommitDiffResponse,
                                     "CommitDiff: exit status 128")
        m = None
        if request.paths:
            m = scmutil.matchfiles(repo, request.paths)
        parser = get_commitDiff_parser(request)
        opts = {b'git': True}
        whitespace = request.ignore_whitespace_change
        # XXX: add support and tests for request.ignore_whitespace_change
        diffopts = diffutil.difffeatureopts(
            repo.ui,
            opts=opts,
            git=True,
            whitespace=whitespace,
        )
        diffchunks = ctx_to.diff(
            ctx_from,
            match=m,
            opts=diffopts
        )
        for header in patchmod.parsepatch(diffchunks):
            from_path, to_path = old_new_file_path(header)
            from_id, to_id = old_new_blob_oids(header, ctx_from, ctx_to)
            old_mode, new_mode = old_new_file_mode(header, ctx_from, ctx_to)
            # For CommitDiffResponse, modes are returned in decimal form
            old_mode, new_mode = int(old_mode, 8), int(new_mode, 8)

            # generator func to yield hunks
            def in_chunks():
                for hunk in header.hunks:
                    with BytesIO() as extracted:
                        hunk.write(extracted)
                        yield extracted.getvalue()

            parser.parse(in_chunks())

            if parser.finished and parser.overflow_marker:
                yield CommitDiffResponse(
                    end_of_patch=True,
                    overflow_marker=True,
                )
                return
            else:
                curr_diff = parser.curr_diff
                response = CommitDiffResponse(
                    from_path=from_path,
                    to_path=to_path,
                    from_id=from_id,
                    to_id=to_id,
                    old_mode=old_mode,
                    new_mode=new_mode,
                    binary=header.binary(),
                    too_large=curr_diff.too_large,
                    collapsed=curr_diff.collapsed,
                )
                patch = curr_diff.patch.getvalue()
                patch_itr = split_batches(patch, DIFF_MSG_SIZE_THRESHOLD)
                for p, eop in iter_boolean_lookahead(patch_itr):
                    response.raw_patch_data = p
                    response.end_of_patch = eop
                    yield response
                    # Use a new response so we don't send other
                    # fields (from_path, ...) over and over
                    response = CommitDiffResponse()
                parser.consume_curr_diff()

    def CommitDelta(self, request: CommitDeltaRequest,
                    context) -> CommitDeltaResponse:
        parsed_request = parse_diff_request(self, request, context)
        _parsed, repo, ctx_from, ctx_to = parsed_request
        if not _parsed:
            return unavailable_error(context, CommitDiffResponse,
                                     "CommitDelta: exit status 128")
        m = None
        if request.paths:
            m = scmutil.matchfiles(repo, request.paths)
        opts = {b'git': True}
        diffopts = diffutil.difffeatureopts(repo.ui, opts=opts, git=True)
        diffchunks = ctx_to.diff(
            ctx_from,
            match=m,
            opts=diffopts
        )

        def in_deltas():
            for header in patchmod.parsepatch(diffchunks):
                from_path, to_path = old_new_file_path(header)
                from_id, to_id = old_new_blob_oids(header, ctx_from, ctx_to)
                old_mode, new_mode = old_new_file_mode(header, ctx_from,
                                                       ctx_to)
                # For CommitDeltaResponse, modes are returned in decimal form
                old_mode, new_mode = int(old_mode, 8), int(new_mode, 8)
                # As per Gitaly/Git behavior, if current Delta is a Rename and
                # if `from_path` is missing in `request.paths`, the other file
                # should be considered as Added instead of a Rename
                if (request.paths and from_path != to_path and
                        from_path not in request.paths):
                    # considering `to_path` as added
                    from_path = to_path
                    from_id = nullhex
                    old_mode = 0
                delta = MsgCommitDelta(
                    from_path=from_path,
                    to_path=to_path,
                    from_id=from_id,
                    to_id=to_id,
                    old_mode=old_mode,
                    new_mode=new_mode,
                )
                yield delta
        for batch in aggregate_flush_batch(in_deltas(), commit_delta_size,
                                           DIFF_MSG_SIZE_THRESHOLD):
            yield CommitDeltaResponse(deltas=batch)

    def RawDiff(self, request: RawDiffRequest,
                context) -> RawDiffResponse:
        parsed_request = parse_diff_request(self, request, context)
        _parsed, repo, ctx_from, ctx_to = parsed_request
        if not _parsed:
            return unknown_error(context, RawDiffResponse, "exit status 128")
        opts = {b'git': True}
        overrides = {
            (b'experimental', b'extendedheader.similarity'): True,
        }
        with repo.ui.configoverride(overrides):
            diffopts = diffutil.diffallopts(repo.ui, opts)
            diffchunks = ctx_to.diff(ctx_from, opts=diffopts)

        # generator func to yield hunks
        def in_chunks():
            for chunk in patchmod.parsepatch(diffchunks):
                header = _insert_blob_index(chunk, ctx_from, ctx_to)
                yield header
                for hunk in chunk.hunks:
                    with BytesIO() as extracted:
                        hunk.write(extracted)
                        yield extracted.getvalue()
        for data in concat_resplit(in_chunks(), WRITE_BUFFER_SIZE):
            yield RawDiffResponse(data=data)

    def RawPatch(self, request: RawPatchRequest,
                 context) -> RawPatchResponse:
        """Yields raw patches between two csets.

        Note: Here, patches are in `hg` format instead of `git`. We decided
        this on the basis of "response is not being parsed at Rails side, and
        directly sent to UI" so that users can import the hg patches.
        """
        parsed_request = parse_diff_request(self, request, context)
        _parsed, repo, ctx_from, ctx_to = parsed_request
        if not _parsed:
            return unknown_error(context, RawPatchResponse, "exit status 128")
        opts = {b'git': True}
        diffopts = diffutil.diffallopts(repo.ui, opts)
        ui = repo.ui
        fm = ui.formatter(b'RawPatch', opts={})
        revs = repo.revs(b'only(%s, %s)', ctx_to, ctx_from)

        def in_chunks():
            for seqno, rev in enumerate(revs):
                ctx = repo[rev]
                itr_data = _exportsingle(repo, ctx, fm, seqno, diffopts)
                for data in itr_data:
                    yield data
        for data in concat_resplit(in_chunks(), WRITE_BUFFER_SIZE):
            yield RawPatchResponse(data=data)

    def DiffStats(self, request: DiffStatsRequest,
                  context) -> DiffStatsResponse:
        parsed_request = parse_diff_request(self, request, context)
        _parsed, repo, ctx_from, ctx_to = parsed_request
        if not _parsed:
            return unavailable_error(context, DiffStatsResponse,
                                     "DiffStats: exit status 128")
        opts = {b'git': True}
        diffopts = diffutil.difffeatureopts(repo.ui, opts=opts, git=True)
        diffchunks = ctx_to.diff(
            ctx_from,
            opts=diffopts
        )

        def in_stats():
            for header in patchmod.parsepatch(diffchunks):
                old_path, path = old_new_file_path(header)
                if old_path == path:
                    old_path = b''
                adds, dels = additions_deletions(header)
                stats = MsgDiffStats(
                    path=path,
                    old_path=old_path,
                    additions=adds,
                    deletions=dels,
                )
                yield stats
        for stats in aggregate_flush_batch(in_stats(), lambda x: 1,
                                           MAX_NUM_STAT_BATCH_SIZE):
            yield DiffStatsResponse(stats=stats)

    def FindChangedPaths(self, request: FindChangedPathsRequest,
                         context) -> FindChangedPathsResponse:
        repo = self.load_repo(request.repository, context)
        csets = []
        for cid in request.commits:
            ctx = gitlab_revision_changeset(repo, parse_diff_request_cid(cid))
            if ctx is None:
                yield not_found(
                    context, FindChangedPathsResponse,
                    'FindChangedPaths: commit: %s can not be '
                    'found' % pycompat.sysstr(cid)
                )
                return
            csets.append(ctx)

        def in_changed_paths():
            for ctx in csets:
                p1 = ctx.p1()
                status = p1.status(ctx)
                for path in _status_paths(status, Status_Type_Map):
                    yield path
            copy = copies.pathcopies(p1, ctx)
            for path in copy:
                yield ChangedPaths(
                    path=path,
                    status=Status_Type_Map['copied']
                )
        for paths in chunked(in_changed_paths()):
            yield FindChangedPathsResponse(paths=paths)


def _status_paths(status, type_map):
    for stype in ['added', 'modified', 'removed']:
        for path in status.__getattribute__(stype):
            yield ChangedPaths(
                path=path,
                status=type_map[stype]
            )


def parse_diff_request_cid(cid):
    """Perform the conversions from a request commit_id to a usable revision.
    """
    if cid == EMPTY_TREE_OID:
        return nullhex
    return pycompat.sysbytes(cid)


def parse_diff_request(servicer, request, context):
    repo = servicer.load_repo(request.repository, context)

    left_cid = parse_diff_request_cid(request.left_commit_id)
    right_cid = parse_diff_request_cid(request.right_commit_id)

    ctx_from = gitlab_revision_changeset(repo, left_cid)
    ctx_to = gitlab_revision_changeset(repo, right_cid)
    if ctx_from is None:
        logger.warning(
            "%s: left_commit_id %r "
            "could not be found", request.__class__.__name__, left_cid)
        return (False, repo, ctx_from, ctx_to)
    if ctx_to is None:
        logger.warning(
            "%s: right_commit_id %r "
            "could not be found", request.__class__.__name__, right_cid)
        return (False, repo, ctx_from, ctx_to)
    return (True, repo, ctx_from, ctx_to)


def old_new_blob_oids(header, old_ctx, new_ctx):
    """Return a tuple of (old, new) blob oids."""
    old_path, new_path = old_new_file_path(header)
    old_bid = new_bid = NULL_BLOB_OID
    if old_path in old_ctx:
        cid = pycompat.sysstr(old_ctx.hex())
        old_bid = blob_oid(None, cid, old_path)
    if new_path in new_ctx:
        cid = pycompat.sysstr(new_ctx.hex())
        new_bid = blob_oid(None, cid, new_path)
    return old_bid, new_bid


def old_new_file_mode(header, old_ctx, new_ctx):
    """Return a tuple of (old, new) file mode."""
    old_path, new_path = old_new_file_path(header)
    old_mode, new_mode = b'0', b'0'
    if old_path in old_ctx:
        old_fctx = old_ctx[old_path]
        old_mode = gitmode[old_fctx.flags()]
    if new_path in new_ctx:
        new_fctx = new_ctx[new_path]
        new_mode = gitmode[new_fctx.flags()]
    return old_mode, new_mode


def old_new_file_path(header):
    """Return a tuple of (old, new) file path."""
    fname = header.filename()
    from_path, to_path = fname, fname
    if len(header.files()) > 1:
        # file is renamed
        from_path, to_path = header.files()
    return from_path, to_path


def additions_deletions(header):
    adds, dels = 0, 0
    for hunk in header.hunks:
        add_count, del_count = hunk.countchanges(hunk.hunk)
        adds += add_count
        dels += del_count
    return adds, dels


def _insert_blob_index(chunk, ctx_from, ctx_to):
    fname = chunk.filename()
    old_bid, new_bid = old_new_blob_oids(chunk, ctx_from, ctx_to)
    indexline = 'index %s..%s' % (old_bid, new_bid)
    indexline = pycompat.sysbytes(indexline)

    # Note: <mode> is required only when it didn't change between
    # the two changesets, otherwise it has a separate line
    if fname in ctx_from and fname in ctx_to:
        oldmode, mode = old_new_file_mode(chunk, ctx_from, ctx_to)
        if mode == oldmode:
            indexline += b' ' + mode
    indexline += b'\n'
    headerlines = chunk.header

    for index, line in enumerate(headerlines[:]):
        if line.startswith(b'--- '):
            headerlines.insert(index, indexline)
            break
    return b''.join(headerlines)


def _exportsingle(repo, ctx, fm, seqno, diffopts):
    """Generator method which yields a bytes stream of exporting `ctx` data.

    This method overwrite upstream mercurial's cmdutil._exportsingle(), as
    the upstream version directly writes the data to stdout and concatenates
    the diff chunks instead of yielding them.
    """
    node = ctx.node()
    parents = [p.node() for p in ctx.parents() if p]
    branch = ctx.branch()

    if parents:
        p1 = parents[0]
    else:
        p1 = nullid

    textlines = []
    textlines.append(b'# HG changeset patch\n')
    textlines.append(b'# User %s\n' % ctx.user())
    textlines.append(b'# Date %d %d\n' % ctx.date())
    textlines.append(b'#      %s\n' % fm.formatdate(ctx.date()))
    if branch and branch != b'default':
        textlines.append(b'# Branch %s\n' % branch)
    textlines.append(b'# Node ID %s\n' % hex(node))
    textlines.append(b'# Parent  %s\n' % hex(p1))
    if len(parents) > 1:
        textlines.append(b'# Parent  %s\n' % hex(parents[1]))

    for headerid in cmdutil.extraexport:
        header = cmdutil.extraexportmap[headerid](seqno, ctx)
        if header is not None:
            textlines.append(b'# %s\n' % header)

    textlines.append(b'%s\n' % ctx.description().rstrip())
    textlines.append(b'\n')
    yield b''.join(textlines)

    chunkiter = patchmod.diff(repo, p1, node, opts=diffopts)
    for chunk in chunkiter:
        yield chunk


def commit_delta_size(delta):
    size = (
        len(delta.from_id) + len(delta.to_id)
        + 4 + 4  # old_mode and new_mode are int, each 4 bytes
        + len(delta.from_path) + len(delta.to_path)
    )
    return size
