from typing import Any

from sqlalchemy import Column, LargeBinary, BigInteger
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple, addTupleType

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.DeclarativeBase import DeclarativeBase


@addTupleType
class EncodedSearchIndexChunk(Tuple, DeclarativeBase, ACIEncodedChunkTupleABC):
    __tablename__ = "EncodedSearchIndexChunk"
    __tupleType__ = searchTuplePrefix + "EncodedSearchIndexChunkTable"

    ENCODED_DATA_KEYWORD_NUM = 0
    ENCODED_DATA_PROPERTY_MAME_NUM = 1
    ENCODED_DATA_OBJECT_IDS_JSON_INDEX = 2

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    chunkKey = Column(Integer, primary_key=True)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (Index("idx_EncodedSearchIndex_chunkKey", chunkKey, unique=True),)

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
    def ckiCreateDeleteEncodedChunk(cls, chunkKey: Any):
        return EncodedSearchIndexChunk(chunkKey=chunkKey)

    @classmethod
    def sqlCoreChunkKeyColumn(cls):
        return cls.__table__.c.chunkKey

    @classmethod
    def sqlCoreLoad(cls, row):
        return EncodedSearchIndexChunk(
            id=row.id,
            chunkKey=row.chunkKey,
            encodedData=row.encodedData,
            encodedHash=row.encodedHash,
            lastUpdate=row.lastUpdate,
        )
