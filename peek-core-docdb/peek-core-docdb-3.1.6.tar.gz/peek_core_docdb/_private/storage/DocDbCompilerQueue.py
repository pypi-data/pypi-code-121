import logging

from sqlalchemy import Column, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_core_docdb._private.PluginNames import docDbTuplePrefix
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class DocDbCompilerQueue(Tuple, DeclarativeBase, ACIProcessorQueueTupleABC):
    __tupleType__ = docDbTuplePrefix + "DocDbChunkQueueTuple"
    __tablename__ = "DocDbChunkQueue"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer, ForeignKey("DocDbModelSet.id", ondelete="CASCADE"), nullable=False
    )

    chunkKey = Column(String, primary_key=True)

    @classmethod
    def sqlCoreLoad(cls, row):
        return DocDbCompilerQueue(
            id=row.id, modelSetId=row.modelSetId, chunkKey=row.chunkKey
        )

    @property
    def ckiUniqueKey(self):
        return self.chunkKey
