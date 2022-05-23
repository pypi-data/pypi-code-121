from abc import abstractmethod


class ACIUpdateDateTupleABC:
    """Chunked Index Object Update Date Tuple

    This tuple represents the state of the chunks in the cache.
    Each chunkKey has a lastUpdateDate as a string, this is used for offline caching
    all the chunks.
    """

    @property
    @abstractmethod
    def ckiUpdateDateByChunkKey(self):
        """Chunk Key Index - Chunk Key

        This property should return the chunk key.

        :return: The value of the chunk key for this value.

        Example code:

                return self.chunkKey

        """
        raise NotImplementedError()
