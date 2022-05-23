import logging

from sqlalchemy import Column, BigInteger
from sqlalchemy import Integer
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_core_search._private.PluginNames import searchTuplePrefix
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class SearchIndexCompilerQueue(Tuple, DeclarativeBase, ACIProcessorQueueTupleABC):
    __tablename__ = "SearchIndexCompilerQueue"
    __tupleType__ = searchTuplePrefix + "SearchIndexCompilerQueueTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chunkKey = Column(Integer, primary_key=True)

    @classmethod
    def sqlCoreLoad(cls, row):
        return SearchIndexCompilerQueue(id=row.id, chunkKey=row.chunkKey)

    @property
    def ckiUniqueKey(self):
        return self.chunkKey
