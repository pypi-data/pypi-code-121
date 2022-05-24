# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from hgitaly.oid import (
    blob_oid,
)
from hgitaly.service.blob import (
    iter_blob_chunks,
)
from hgitaly.stream import WRITE_BUFFER_SIZE

from hgitaly.tests.common import (
    make_empty_repo,
)

from hgitaly.stub.blob_pb2 import (
    GetBlobRequest,
    GetBlobsRequest,
)
from hgitaly.stub.blob_pb2_grpc import BlobServiceStub


def test_get_blob(grpc_channel, server_repos_root):
    grpc_stub = BlobServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def do_rpc(oid, limit=-1):
        request = GetBlobRequest(repository=grpc_repo,
                                 oid=oid,
                                 limit=limit)
        return [resp for resp in grpc_stub.GetBlob(request)]

    small = wrapper.write_commit('foo', content='some content')
    oid = blob_oid(wrapper.repo, small.hex().decode(), b'foo')
    resps = do_rpc(oid)

    assert len(resps) == 1
    assert resps[0].data == b'some content'
    assert resps[0].size == 12
    assert resps[0].oid == oid

    resps = do_rpc(oid, limit=4)
    assert len(resps) == 1
    assert resps[0].data == b'some'
    assert resps[0].size == 12
    assert resps[0].oid == oid

    large_data = b'\xca\xfe' * 1024 * 65  # 1024 more than WRITE_BUFFER_SIZE
    large = wrapper.write_commit('foo', content=large_data, message='largebin')
    oid = blob_oid(wrapper.repo, large.hex().decode(), b'foo')
    resps = do_rpc(oid)

    assert len(resps) == 2
    assert resps[0].data == large_data[:WRITE_BUFFER_SIZE]
    assert resps[0].size == len(large_data)
    assert resps[0].oid == oid

    assert resps[1].data == b'\xca\xfe' * 1024
    assert resps[1].size == 0
    assert resps[1].oid == ''


def test_get_blobs(grpc_channel, server_repos_root):
    grpc_stub = BlobServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    repo = wrapper.repo
    RevisionPath = GetBlobsRequest.RevisionPath

    def do_rpc(rev_paths, limit=-1):
        request = GetBlobsRequest(
            repository=grpc_repo,
            revision_paths=[RevisionPath(revision=rev, path=path)
                            for rev, path in rev_paths],
            limit=limit)
        return [resp for resp in grpc_stub.GetBlobs(request)]

    wrapper.write_commit('foo', content='some content')
    two_files = wrapper.write_commit('bar', content='bar content')
    tip_hex = two_files.hex().decode()
    resps = do_rpc([(tip_hex, b'foo'),
                    (tip_hex, b'bar'),
                    (b'unknown-rev', b'foo'),
                    (tip_hex, b'unknown-file')
                    ])

    assert len(resps) == 4
    assert resps[0].data == b'some content'
    assert resps[0].size == 12
    assert resps[0].oid == blob_oid(repo, tip_hex, b'foo')

    assert resps[1].data == b'bar content'
    assert resps[1].size == 11
    assert resps[1].oid == blob_oid(repo, tip_hex, b'bar')

    assert not resps[2].oid
    assert not resps[3].oid

    resps = do_rpc([(tip_hex, b'foo'), (tip_hex, b'bar')], limit=4)
    assert len(resps) == 2
    assert resps[0].data == b'some'
    assert resps[0].size == 12
    assert resps[0].oid == blob_oid(repo, tip_hex, b'foo')

    assert resps[1].data == b'bar '
    assert resps[1].size == 11
    assert resps[1].oid == blob_oid(repo, tip_hex, b'bar')


def test_iter_blob_chunks():
    """Complements: edge cases etc."""

    assert list(iter_blob_chunks(b'aabbc', chunk_size=2)) == [
        (b'aa', True),
        (b'bb', False),
        (b'c', False),
    ]
    assert list(iter_blob_chunks(b'aabb', chunk_size=2)) == [
        (b'aa', True),
        (b'bb', False),
    ]
    assert list(iter_blob_chunks(b'')) == [(b'', True)]
    assert list(iter_blob_chunks(b'aabb', chunk_size=4)) == [(b'aabb', True)]
