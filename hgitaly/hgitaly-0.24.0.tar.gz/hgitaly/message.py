# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""High level utilities for Gitaly protocol messages."""

from mercurial.utils import stringutil as hg_stringutil
from mercurial import (
    node,
    pycompat,
)

from .stub.shared_pb2 import (
    CommitAuthor,
    GitCommit,
    SignatureType,
    Tag,
)
from .stub.commit_pb2 import (
    ListLastCommitsForTreeResponse,
)
from google.protobuf.text_format import MessageToString
from google.protobuf.timestamp_pb2 import Timestamp


class Logging:
    """Wrapper of requests and responses for sensible logging.

    Still has the formatting happen lazily, only if the message
    is emitted. We still pay the price of at least one instantiation though.
    """

    def __init__(self, message):
        self.msg = message

    def __repr__(self):
        return '%s { %s }' % (self.msg.__class__.__name__,
                              MessageToString(self.msg, as_one_line=True))

    __str__ = __repr__


def commit_author(ctx):
    """Produce a `GitCommit` message from a :class:`changectx` instance.
    """
    auth = ctx.user()
    date = Timestamp()
    # hg time resolution is the second, see
    # https://www.mercurial-scm.org/wiki/ChangeSet
    seconds, offset = ctx.date()
    date.FromSeconds(int(seconds))
    if offset <= 0:
        # Mercurial sign convention is opposite of UTC+2 etc.
        tz_sign = b'+'
        offset_abs = -offset
    else:
        tz_sign = b'-'
        offset_abs = offset

    # Mercurial offset is in seconds
    tz_hours = offset_abs // 3600
    tz_minutes = (offset_abs % 3600) // 60

    return CommitAuthor(
        email=hg_stringutil.email(auth),
        name=hg_stringutil.person(auth),
        date=date,
        timezone=b"%s%02d%02d" % (tz_sign, tz_hours, tz_minutes),
        )


def commit(ctx):
    """Return :class:`GitCommit` object from Mercurial :class:`changectx`.

    subject and body are as in gitaly/internal/git/log/commitmessage.go::

      var body string
      if split := strings.SplitN(commitString, "\n\n", 2); len(split) == 2 {
          body = split[1]
      }
      subject := strings.TrimRight(strings.SplitN(body, "\n", 2)[0], "\r\n")

    See also slightly different stripping gitlab/lib/gitlab/git/commit.rb::

        message_split = raw_commit.message.split("\n", 2)
        Gitaly::GitCommit.new(
          id: raw_commit.oid,
          subject: message_split[0] ? message_split[0].chomp.b : "",
          body: raw_commit.message.b,
          parent_ids: raw_commit.parent_ids,
          author: gitaly_commit_author_from_rugged(raw_commit.author),
          committer: gitaly_commit_author_from_rugged(raw_commit.committer)
        )

    Special case for caller convenience::

        >>> commit(None) is None
        True
    """
    if ctx is None:
        return None

    descr = ctx.description()
    author = commit_author(ctx)
    return GitCommit(id=ctx.hex(),
                     subject=descr.split(b'\n', 1)[0].rstrip(b'\r\n'),
                     body=descr,
                     body_size=len(descr),
                     parent_ids=[p.hex().decode()
                                 for p in ctx.parents()
                                 if p.rev() != node.nullrev],
                     author=author,
                     committer=author,
                     )


def tag(name, target, tagging=None, signature_type=None):
    """Produce a :class:`Tag` instance

    :param target: a :class:`changectx` for the target of the tag
    :param tagging: optional :class:`changectx` for the changeset that
                    sets the tag.
    :pram signature_type: a :class:`SignatureType` or ``None``.
    """
    if signature_type is None:
        signature_type = SignatureType.NONE

    if tagging is None:
        tag_id = message = tag_author = None
        message_size = 0
    else:
        # TODO SPEC comment in `shared.proto` says the message will be
        # nullified if above a certain size and the size will be carried over,
        # but it doesn't say whose responsibility it is to do that,
        # nor how that threshold is to be determined
        # (information should be found by reading Gitaly Golang source).
        message = tagging.description()
        message_size = len(message)
        tag_id = pycompat.sysstr(tagging.hex())
        tag_author = commit_author(tagging)

    return Tag(name=name,
               id=tag_id,
               target_commit=commit(target),
               message=message,
               message_size=message_size,
               tagger=tag_author,
               signature_type=signature_type
               )


CommitForTree = ListLastCommitsForTreeResponse.CommitForTree


def commit_for_tree(changeset, path):
    """Message indicating the last changeset having modified a path"""
    return CommitForTree(commit=commit(changeset), path_bytes=path)
