from abc import abstractmethod
from typing import Any


class ACIEncodedChunkTupleABC:
    @property
    @abstractmethod
    def ckiHasEncodedData(self) -> bool:
        """Chunk Key Index - Has Encoded Data

        :return: Is there data in this chunk? dataless chunks are deletes

        Example code:

                return bool(self.encodedData)

        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def ckiChunkKey(self):
        """Chunk Key Index - Chunk Key

        This property should return the chunk key.

        :return: The value of the chunk key for this value.

        Example code:

                return self.chunkKey

        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def ckiLastUpdate(self):
        """Chunk Key Index - Chunk Key

        This property should return the chunk key.

        :return: The value of the chunk key for this value.

        Example code:

                return self.chunkKey

        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def ckiCreateDeleteEncodedChunk(cls, chunkKey: Any):
        """Chunk Key Index - Create Delete Encoded Chunk

        This method should return a new EncodedChunkTuple with just the chunk
        key populated.

        :return: The column

        Example code:

                return cls.__table__.c.chunkKey

        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def sqlCoreChunkKeyColumn(cls):
        """SQL Core - Chunk Key Column

        This method should return the SQL Core column

        :return: The column

        Example code:

                return cls.__table__.c.chunkKey

        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def sqlCoreLoad(cls, row):
        """SQL Core - Load

        This method creates the declarative from an SQL core query.
        There is a lot of overhead from using the ORM to load this
        then expunging it. So instead an SQLCore query then create the tuple.

        Example code:

            return EncodedSearchIndexChunk(id=row.id,
                                            chunkKey=row.chunkKey,
                                            encodedData=row.encodedData,
                                            encodedHash=row.encodedHash,
                                            lastUpdate=row.lastUpdate)
        """
        raise NotImplementedError()
