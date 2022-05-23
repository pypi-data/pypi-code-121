import logging

from sqlalchemy import Column, Index, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class BranchIndexCompilerQueue(Tuple, DeclarativeBase, ACIProcessorQueueTupleABC):
    __tablename__ = "BranchIndexCompilerQueue"
    __tupleType__ = diagramTuplePrefix + "BranchIndexCompilerQueueTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer,
        ForeignKey("ModelSet.id", ondelete="CASCADE"),
        nullable=False,
        autoincrement=True,
    )

    chunkKey = Column(String, primary_key=True)

    __table_args__ = (
        Index(
            "idx_BICompQueue_modelSetId_chunkKey", modelSetId, chunkKey, unique=False
        ),
    )

    @classmethod
    def sqlCoreLoad(cls, row):
        return BranchIndexCompilerQueue(
            id=row.id, modelSetId=row.modelSetId, chunkKey=row.chunkKey
        )

    @property
    def ckiUniqueKey(self):
        return self.chunkKey
