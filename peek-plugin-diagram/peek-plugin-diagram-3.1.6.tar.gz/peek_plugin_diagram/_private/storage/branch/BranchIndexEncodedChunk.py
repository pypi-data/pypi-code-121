import logging

from sqlalchemy import Column, LargeBinary, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_diagram._private.storage.ModelSet import ModelSet

logger = logging.getLogger(__name__)


@addTupleType
class BranchIndexEncodedChunk(Tuple, DeclarativeBase, ACIEncodedChunkTupleABC):
    __tablename__ = "BranchIndexEncodedChunk"
    __tupleType__ = diagramTuplePrefix + "BranchIndexEncodedChunkTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer, ForeignKey("ModelSet.id", ondelete="CASCADE"), nullable=False
    )
    modelSet = relationship(ModelSet)

    chunkKey = Column(String, nullable=False)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index(
            "idx_BranchIndexEnc_modelSetId_chunkKey", modelSetId, chunkKey, unique=False
        ),
    )

    @property
    def ckiChunkKey(self):
        return self.chunkKey

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedData)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

    @classmethod
    def ckiCreateDeleteEncodedChunk(cls, chunkKey: str):
        return BranchIndexEncodedChunk(indexBucket=chunkKey)

    @classmethod
    def sqlCoreChunkKeyColumn(cls):
        return cls.__table__.c.chunkKey

    @classmethod
    def sqlCoreLoad(cls, row):
        return BranchIndexEncodedChunk(
            id=row.id,
            modelSetId=row.modelSetId,
            chunkKey=row.chunkKey,
            encodedData=row.encodedData,
            encodedHash=row.encodedHash,
            lastUpdate=row.lastUpdate,
        )
