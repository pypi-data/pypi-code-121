from abc import ABCMeta
from typing import List, Any, Optional, Type

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.LoadPayloadPgUtil import (
    getTuplesPayloadBlocking,
    LoadPayloadTupleResult,
)
from sqlalchemy import select
from sqlalchemy.sql import Select


class ACIChunkLoadRpcABC(metaclass=ABCMeta):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    # -------------
    def ckiInitialLoadChunksBlocking(
        self, offset: int, count: int, Declarative: Type[ACIEncodedChunkTupleABC]
    ) -> List[Any]:
        """Chunked Key Index - Initial Load Chunks Blocking

        This method is used to load the initial set of chunks from the server
        to the client.

        """
        table = Declarative.__table__
        session = self._dbSessionCreator()
        try:
            sql = (
                select([table])
                .order_by(Declarative.sqlCoreChunkKeyColumn())
                .offset(offset)
                .limit(count)
            )

            sqlData = session.execute(sql).fetchall()

            results: List[ACIEncodedChunkTupleABC] = [
                Declarative.sqlCoreLoad(item) for item in sqlData
            ]

            return results

        finally:
            session.close()

    # -------------
    def ckiInitialLoadChunksPayloadBlocking(
        self,
        offset: int,
        count: int,
        Declarative: Type[ACIEncodedChunkTupleABC],
        sql: Optional[Select] = None,
    ) -> Optional[bytes]:
        """Chunked Key Index - Initial Load Chunks Blocking

        This method is used to load the initial set of chunks from the server
        to the client.

        """
        if sql is None:
            table = Declarative.__table__
            sql = (
                select([table])
                .order_by(Declarative.sqlCoreChunkKeyColumn())
                .offset(offset)
                .limit(count)
            )

        result: LoadPayloadTupleResult = getTuplesPayloadBlocking(
            self._dbSessionCreator, sql, Declarative.sqlCoreLoad, fetchSize=count
        )

        return result.encodedPayload
