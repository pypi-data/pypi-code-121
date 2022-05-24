# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import itertools

from .stub.shared_pb2 import (
    PaginationCursor,
)

# default as in Gitaly's internal/helper/chunk/chunker.go
DEFAULT_CHUNK_SIZE = 20


def chunked(iterable, size=DEFAULT_CHUNK_SIZE, limit=None):
    """Return a generator of chunks out of given iterable.

    >>> [chunk for chunk in chunked(range(3), size=2)]
    [[0, 1], [2]]
    >>> [chunk for chunk in chunked(range(4), size=2)]
    [[0, 1], [2, 3]]

    :param limit: maximum total number of results (unlimited if evaluates to
                  ``False``

    >>> [chunk for chunk in chunked(range(7), size=2, limit=2)]
    [[0, 1]]
    """
    chunk = []
    if limit:
        iterable = itertools.islice(iterable, 0, limit)
    for i, val in enumerate(iterable):
        if i != 0 and i % size == 0:
            yield chunk
            chunk = []
        chunk.append(val)

    yield chunk


def chunked_with_cursor(message_class, iterable, next_cursor, builder,
                        size=DEFAULT_CHUNK_SIZE, limit=None):
    """Iterate in chunks and generate gRPC messages with pagination cursor.

    It is important that the pagination cursor is present only on the
    first message. Using the default value `PaginationCursor()` instead can be
    a breaking mistake (see hgitaly#91 for the gory details).

    This helper is there to help do the right thing, not to make it
    especially simpler for the caller.
    """
    first = True
    for chunk in chunked(iterable):
        fields = builder(chunk)
        if first:
            fields['pagination_cursor'] = PaginationCursor(
                next_cursor=next_cursor)
            first = False
        yield message_class(**fields)
