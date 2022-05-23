import logging
from abc import ABCMeta
from typing import List, Optional, Dict

from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.VortexFactory import VortexFactory, NoVortexException

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_base.PeekVortexUtil import peekBackendNames
from peek_plugin_base.storage.RunPyInPg import runPyInPg


class ACIChunkUpdateHandlerABC(metaclass=ABCMeta):
    """Client Chunked Index Update Controller

    This controller handles sending updates the the client.

    It uses lower level Vortex API

    It does the following a broadcast to all clients:

    1) Sends grid updates to the clients

    2) Sends Lookup updates to the clients

    """

    _ChunkedTuple: ACIEncodedChunkTupleABC = None
    _updateFromServerFilt: Dict = None
    _logger: logging.Logger = None

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    def sendChunks(self, chunkKeys: List[str]) -> None:
        """Send Location Indexes

        Send grid updates to the client services

        :param chunkKeys: A list of object buckets that have been updated
        :returns: Nochunked
        """

        if not chunkKeys:
            return

        vortexNamesToSendTo = set(peekBackendNames) & set(
            VortexFactory.getRemoteVortexName()
        )
        if not vortexNamesToSendTo:
            self._logger.debug(
                "No clients are online to send the chunked chunk to, %s", chunkKeys
            )
            return

        def send(vortexMsg: bytes):
            if vortexMsg:
                for vortexName in vortexNamesToSendTo:
                    VortexFactory.sendVortexMsg(vortexMsg, destVortexName=vortexName)

        d: Deferred = self._loadChunks(chunkKeys)
        d.addCallback(send)
        d.addErrback(self._sendErrback, chunkKeys)

    def _sendErrback(self, failure, chunkKeys):

        if failure.check(NoVortexException):
            self._logger.debug(
                "No clients are online to send the chunked chunk to, %s", chunkKeys
            )
            return

        vortexLogFailure(failure, self._logger)

    @inlineCallbacks
    def _loadChunks(self, chunkKeys: List[str]) -> Optional[bytes]:
        """Load Chunks"""
        assert chunkKeys, "we must have some chunkKeys"

        encodedPayload = yield runPyInPg(
            self._logger, self._dbSessionCreator, self._loadChunksInPg, None, chunkKeys
        )

        return encodedPayload.encode()

    @classmethod
    def _makeLoadSql(cls, chunkKeys: List[str]):
        table = cls._ChunkedTuple.__table__

        return select([table]).where(
            cls._ChunkedTuple.sqlCoreChunkKeyColumn().in_(chunkKeys)
        )

    @classmethod
    def _loadChunksInPg(
        cls, plpy, chunkKeys: List[str], *args, **kwargs
    ) -> Optional[bytes]:
        """Load Chunks in PostGreSQL

        This method is dynamically imported into PostGreSQL and run in the
        database with the plpython3u extension

        """
        # ---------------
        # Prepare the SQL
        sql = cls._makeLoadSql(chunkKeys)

        sqlQry = str(
            sql.compile(
                dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
            )
        )

        # ---------------
        # Turn a row["val"] into a row.val
        class Wrap:
            row = None

            def __getattr__(self, name):
                return self.row[name]

        wrap = Wrap()

        # ---------------
        # Iterate through and load the tuples
        results: List[ACIEncodedChunkTupleABC] = []

        cursor = plpy.cursor(sqlQry)
        while True:
            rows = cursor.fetch(len(chunkKeys))
            if not rows:
                break
            for row in rows:
                wrap.row = row
                results.append(cls._ChunkedTuple.sqlCoreLoad(wrap))

        # ---------------
        # Process the results, create blank grids where the grid has been deleted

        deletedChunkKeys = set(chunkKeys) - set([r.ckiChunkKey for r in results])

        for chunkKey in deletedChunkKeys:
            results.append(cls._ChunkedTuple.ckiCreateDeleteEncodedChunk(chunkKey))

        if not results:
            return None

        return (
            Payload(filt=cls._updateFromServerFilt, tuples=results)
            .makePayloadEnvelope(compressionLevel=3)
            .toVortexMsg()
            .decode()
        )
