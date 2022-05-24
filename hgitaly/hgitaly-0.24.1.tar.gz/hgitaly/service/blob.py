# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import io
import logging

from mercurial import (
    error,
)

from ..stub.shared_pb2 import (
    ObjectType,
)
from ..stub.blob_pb2 import (
    GetBlobRequest,
    GetBlobResponse,
    GetBlobsRequest,
    GetBlobsResponse,
)
from ..stub.blob_pb2_grpc import BlobServiceServicer

from ..oid import (
    blob_oid,
    extract_blob_oid,
)
from ..file_context import git_perms
from ..revision import gitlab_revision_changeset
from ..servicer import HGitalyServicer
from ..stream import WRITE_BUFFER_SIZE

logger = logging.getLogger(__name__)


class BlobServicer(BlobServiceServicer, HGitalyServicer):
    """BlobService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def GetBlob(self, request: GetBlobRequest,
                context) -> GetBlobResponse:
        logger.info("GetBlob request=%r", request)
        # TODO return Unavailable for readLimit = 0, as Gitaly does
        repo = self.load_repo(request.repository, context).unfiltered()
        chgs_id, path = extract_blob_oid(repo, request.oid)
        changeset = repo[chgs_id.encode()]  # TODO error treatment
        filectx = changeset.filectx(path)  # TODO error treatment
        size = filectx.size()
        data = filectx.data()
        if request.limit != -1:
            data = data[:request.limit]

        for chunk, is_first in iter_blob_chunks(data):
            resp_dict = dict(data=chunk)
            if is_first:
                resp_dict.update(size=size, oid=request.oid)
            yield GetBlobResponse(**resp_dict)

    def GetBlobs(self, request: GetBlobsRequest, context) -> GetBlobsResponse:
        revision_paths = [(rev_path.revision, rev_path.path)
                          for rev_path in request.revision_paths]

        logger.debug("GetBlobs repo relative_path=%r, revision_paths=%r",
                     request.repository.relative_path,
                     revision_paths,
                     )
        repo = self.load_repo(request.repository, context).unfiltered()
        limit = request.limit

        for rev, path in revision_paths:
            # TODO it's probably an oversight on upstream side that revision
            # is `str` and not `bytes`, but then, what would be the encoding?
            changeset = gitlab_revision_changeset(repo,
                                                  rev.encode('utf-8', 'ignore')
                                                  )
            if changeset is None:
                filectx = None
            else:
                try:
                    filectx = changeset.filectx(path)
                except error.ManifestLookupError:
                    filectx = None

            if changeset is None or filectx is None:
                # missing file is represented by oid=''
                # (see comment in blob.proto)
                yield GetBlobsResponse(path=path, revision=rev)
                continue

            filectx = changeset.filectx(path)
            oid = blob_oid(repo, changeset.hex().decode(), path)

            size = filectx.size()
            data = filectx.data()
            if limit != -1:
                data = data[:limit]

            for chunk, first in iter_blob_chunks(data):
                # is_submodule will be False, because that's the default
                # should at least be documented somewhere though
                dict_resp = dict(data=chunk)

                if first:
                    dict_resp.update(size=size,
                                     oid=oid,
                                     path=path,
                                     revision=rev,
                                     type=ObjectType.BLOB,
                                     mode=git_perms(filectx),
                                     )

                yield GetBlobsResponse(**dict_resp)


def iter_blob_chunks(data, chunk_size=WRITE_BUFFER_SIZE):
    """Generator for chunks of Blob data.


    The first chunk always bear the Blob oid and the full Blob size.
    The next ones don't have them (i.e., they have the gRPC default values)
    """
    # better than reimplementing our own cursor system
    reader = io.BytesIO(data)

    is_first = True
    while True:
        chunk = reader.read(chunk_size)
        # send first response even if empty
        if is_first or chunk:
            yield chunk, is_first
        else:
            # the break statement would be equivalent, but would appears
            # uncovered. If someone has the courage, it could be a
            # bug to report in coverage 5.5
            return
        is_first = False
