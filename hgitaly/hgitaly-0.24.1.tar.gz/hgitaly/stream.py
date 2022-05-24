# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Quoting from Gitaly 13.4:
# //  WriteBufferSize is the largest []byte that Write() will pass
# //  to its underlying send function. This value can be changed
# //  at runtime using the GITALY_STREAMIO_WRITE_BUFFER_SIZE environment
# //  variable.
#
# var WriteBufferSize = 128 * 1024
#
# As of GitLab 13.4, the environment variable is parsed with
# `strconv.ParseInt(value, 0, 32)`.
# Quoting https://golang.org/pkg/strconv/#ParseInt:
#     If the base argument is 0, the true base is implied by
#     the string's prefix: 2 for "0b", 8 for "0" or "0o", 16 for "0x",
#     and 10 otherwise. Also, for argument base 0 only,
#     underscore characters are permitted as defined by the
#     Go syntax for integer literals.
import contextlib
import os
import tempfile


def concat_resplit(in_chunks, out_chunks_size):
    """Generator that aggregate incoming chunks of bytes and yield chunks with
    the wished size.

    in_chunks: an iterator of chunk of bytes of arbitrary sizes
    out_chunks_size: size of chunks to be yield, except last one
    """
    data = b''
    for chunk in in_chunks:
        data += chunk
        while len(data) > out_chunks_size:
            yield data[:out_chunks_size]
            data = data[out_chunks_size:]
    yield data


def split_batches(in_bytes, out_bytes_size):
    """Generator that yield in_bytes in fixed size batches.

    in_bytes: bytes of arbitrary size
    out_bytes_size: size of chunks to be yield, except last one
    """
    while len(in_bytes) > out_bytes_size:
        yield in_bytes[:out_bytes_size]
        in_bytes = in_bytes[out_bytes_size:]
    yield in_bytes


def iter_boolean_lookahead(itr):
    """Generator that yield tuple (value, is_last_value)."""
    try:
        prev = next(itr)
    except StopIteration:
        return

    for value in itr:
        yield prev, False
        prev = value
    yield prev, True


def aggregate_flush_batch(itr, custom_size_func, out_batch_size):
    """Generator that yields `itr` values in batch after the size cross
    a certain limit, where size of each value is calculated using a
    `custom_size_func`.

    itr: an iterator of values that to be yield in batch
    custom_size_func: a func to calculate size of each value
    out_batch_size: threshold of a batch size
    """
    batch = []
    batch_size = 0
    for val in itr:
        batch.append(val)
        batch_size += custom_size_func(val)
        if batch_size > out_batch_size:
            yield batch
            batch = []
            batch_size = 0
    yield batch


def parse_int(s):
    """Parse integer string representations, as Golangs `strconf.ParseInt`

    # TODO check at least octal and hex syntaxes
    >>> parse_int('10')
    10
    """
    return int(s)


def env_write_buffer_size():
    str_val = os.environ.get('GITALY_STREAMIO_WRITE_BUFFER_SIZE')
    if not str_val:
        return 128 * 1024
    return parse_int(str_val)


WRITE_BUFFER_SIZE = env_write_buffer_size()
"""In Gitaly, there is a general binary chunking system,
used in many places, notably all binary content producers (diff, blame,
blob, archive...)

Extract from streamio/stream.go:

// WriteBufferSize is the largest []byte that Write() will pass to its
// underlying send function. This value can be changed at runtime using
// the GITALY_STREAMIO_WRITE_BUFFER_SIZE environment variable.
var WriteBufferSize = 128 * 1024
"""


@contextlib.contextmanager
def streaming_request_tempfile_extract(requests, context,
                                       data_attr='data',
                                       first_request_handler=None):
    """Extract data from a streaming request.

    It is a a common Gitaly pattern for streaming requests with binary
    data to bear other information in the first request message only.

    This context manager extracts all the binary data in a
    :class:`NamedTemporaryFile` and calls `first_request_handler` to
    perform actions from the first request message.

    The provided Python context is the (first_result, temporary file) pair,
    where `first_result` is the return value of `first_request_handler`.
    """
    with tempfile.NamedTemporaryFile(mode='wb+',
                                     buffering=WRITE_BUFFER_SIZE) as tmpf:
        first_request = True
        first_result = None
        for req in requests:
            if first_request and first_request_handler is not None:
                first_result = first_request_handler(req, context)
                first_request = False
            tmpf.write(req.data)
        tmpf.seek(0)

        yield first_result, tmpf


def slice_binary_file(path, nb_chunks):
    """Generator for the content of binary file at path.

    Suboptimal implementation currently used in tests only (loads
    file content in RAM).
    Must be improved for use in main code (not so likely because main code
    would be more interested in a fixed chunk size).
    """
    with open(path, 'rb') as fobj:
        data = fobj.read()

    chunk_size = len(data) // nb_chunks
    for i in range(0, nb_chunks):
        yield data[i * chunk_size:(i + 1) * chunk_size]
