import logging

from sqlalchemy import Column, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary
from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from .DeclarativeBase import DeclarativeBase
from .Display import DispBase
from .ModelSet import ModelCoordSet

logger = logging.getLogger(__name__)


@addTupleType
class GridKeyCompilerQueue(Tuple, DeclarativeBase, ACIProcessorQueueTupleABC):
    __tablename__ = "GridKeyCompilerQueue"
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    gridKey = Column(String(30), primary_key=True)
    coordSetId = Column(
        Integer, ForeignKey("ModelCoordSet.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        Index("idx_GKCompQueue_coordSetId_gridKey", coordSetId, gridKey, unique=False),
    )

    @classmethod
    def sqlCoreLoad(cls, row):
        return GridKeyCompilerQueue(
            id=row.id, coordSetId=row.coordSetId, gridKey=row.gridKey
        )

    @property
    def ckiUniqueKey(self):
        return self.gridKey


@addTupleType
class GridKeyIndex(Tuple, DeclarativeBase):
    __tablename__ = "GridKeyIndex"
    __tupleType__ = diagramTuplePrefix + __tablename__

    gridKey = Column(String(30), primary_key=True)
    dispId = Column(
        BigInteger, ForeignKey("DispBase.id", ondelete="CASCADE"), primary_key=True
    )

    disp = relationship(DispBase)

    coordSetId = Column(
        Integer, ForeignKey("ModelCoordSet.id", ondelete="CASCADE"), nullable=False
    )
    coordSet = relationship(ModelCoordSet)

    __table_args__ = (
        Index("idx_GridKeyIndex_gridKey", gridKey, unique=False),
        Index("idx_GridKeyIndex_dispId", dispId, unique=False),
        Index("idx_GridKeyIndex_coordSetId", coordSetId, unique=False),
    )


@addTupleType
class GridKeyIndexCompiled(Tuple, DeclarativeBase, ACIEncodedChunkTupleABC):
    __tablename__ = "GridKeyIndexCompiled"
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    gridKey = Column(String(30), nullable=False)
    encodedGridTuple = Column(PeekLargeBinary, nullable=False)
    lastUpdate = Column(String(50), nullable=False)

    coordSetId = Column(
        Integer, ForeignKey("ModelCoordSet.id", ondelete="CASCADE"), nullable=False
    )
    coordSet = relationship(ModelCoordSet)

    __table_args__ = (
        Index("idx_GKIndexUpdate_coordSetId", coordSetId, unique=False),
        Index("idx_GKIndexUpdate_gridKey", gridKey, unique=True),
    )

    @property
    def ckiChunkKey(self):
        return self.gridKey

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedGridTuple)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

    @classmethod
    def ckiCreateDeleteEncodedChunk(cls, chunkKey: str):
        from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import (
            EncodedGridTuple,
        )

        return EncodedGridTuple(gridKey=chunkKey)

    @classmethod
    def sqlCoreChunkKeyColumn(cls):
        return cls.__table__.c.gridKey

    @classmethod
    def sqlCoreLoad(cls, row):
        from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import (
            EncodedGridTuple,
        )

        return EncodedGridTuple(
            gridKey=row.gridKey,
            encodedGridTuple=row.encodedGridTuple,
            lastUpdate=row.lastUpdate,
        )
