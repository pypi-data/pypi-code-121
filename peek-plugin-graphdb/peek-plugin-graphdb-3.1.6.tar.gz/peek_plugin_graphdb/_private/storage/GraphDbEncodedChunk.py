import logging

from sqlalchemy import Column, LargeBinary, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import (
    GraphDbEncodedChunkTuple,
)
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


class GraphDbEncodedChunk(DeclarativeBase, ACIEncodedChunkTupleABC):
    __tablename__ = "GraphDbEncodedChunk"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer, ForeignKey("GraphDbModelSet.id", ondelete="CASCADE"), nullable=False
    )
    modelSet = relationship(GraphDbModelSet, lazy=False)

    chunkKey = Column(String, nullable=False)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_Chunk_modelSetId_chunkKey", modelSetId, chunkKey, unique=False),
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
        return GraphDbEncodedChunkTuple(chunkKey=chunkKey)

    @classmethod
    def sqlCoreChunkKeyColumn(cls):
        return cls.__table__.c.chunkKey

    @classmethod
    def sqlCoreLoad(cls, row):
        return GraphDbEncodedChunkTuple(
            modelSetKey=row.key,
            chunkKey=row.chunkKey,
            encodedData=row.encodedData,
            encodedHash=row.encodedHash,
            lastUpdate=row.lastUpdate,
        )
