import logging
from abc import ABCMeta
from typing import Optional

from peek_abstract_chunked_data_loader.private.tuples.ACDLChunkLoadStateTupleABC import (
    ACDLChunkLoadStateTupleABC,
)
from peek_plugin_base.storage.LoadPayloadPgUtil import (
    getTuplesPayloadBlocking,
    LoadPayloadTupleResult,
)
from sqlalchemy import select
from sqlalchemy.sql import Select

logger = logging.getLogger(__name__)


class ACDLRpcForAgentImportABC(metaclass=ABCMeta):
    _StateTupleDeclarative: ACDLChunkLoadStateTupleABC = None

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    # -------------
    def adlInitialLoadOfStatePayloadBlocking(
        self, offset: int, count: int, sql: Optional[Select] = None
    ) -> Optional[bytes]:
        """Chunked Key Index - Initial Load Chunks Blocking

        This method is used to load the initial set of chunks from the server
        to the client.

        """
        if sql is None:
            table = self._StateTupleDeclarative.__table__
            sql = (
                select([table])
                .order_by(self._StateTupleDeclarative.sqlCoreIdColumn())
                .offset(offset)
                .limit(count)
            )

        result: LoadPayloadTupleResult = getTuplesPayloadBlocking(
            self._dbSessionCreator,
            sql,
            self._StateTupleDeclarative.sqlCoreLoad,
            fetchSize=count,
        )

        return result.encodedPayload

    # -------------
    def adlStoreStateInfoTuple(
        self, item: _StateTupleDeclarative
    ) -> _StateTupleDeclarative:
        """Store the Info Tuples"""

        session = self._dbSessionCreator()
        try:
            if item.id is None:
                session.add(item)
            else:
                item = session.merge(item)
            session.commit()
            session.refresh(item)
            session.expunge_all()
            return item

        finally:
            session.close()
