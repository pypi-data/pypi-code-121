import logging

from sqlalchemy import Column, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class ItemKeyIndexCompilerQueue(Tuple, DeclarativeBase, ACIProcessorQueueTupleABC):
    __tablename__ = "ItemKeyIndexCompilerQueue"
    __tupleType__ = graphDbTuplePrefix + "ItemKeyIndexCompilerQueueTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer,
        ForeignKey("GraphDbModelSet.id", ondelete="CASCADE"),
        nullable=False,
        autoincrement=True,
    )

    chunkKey = Column(String, primary_key=True)

    @classmethod
    def sqlCoreLoad(cls, row):
        return ItemKeyIndexCompilerQueue(
            id=row.id, modelSetId=row.modelSetId, chunkKey=row.chunkKey
        )

    @property
    def ckiUniqueKey(self):
        return self.chunkKey
