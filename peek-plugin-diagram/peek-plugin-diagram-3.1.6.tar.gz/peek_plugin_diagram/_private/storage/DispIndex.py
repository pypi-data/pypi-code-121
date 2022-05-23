from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.DeclarativeBase import DeclarativeBase
from sqlalchemy import Column, Index, BigInteger
from vortex.Tuple import addTupleType, Tuple


@addTupleType
class DispIndexerQueue(Tuple, DeclarativeBase, ACIProcessorQueueTupleABC):
    __tablename__ = "DispCompilerQueue"
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dispId = Column(BigInteger, primary_key=True)

    __table_args__ = (Index("idx_DispCompQueue_dispId", dispId, unique=False),)

    @classmethod
    def sqlCoreLoad(cls, row):
        return DispIndexerQueue(id=row.id, dispId=row.dispId)

    @property
    def ckiUniqueKey(self):
        return self.dispId
