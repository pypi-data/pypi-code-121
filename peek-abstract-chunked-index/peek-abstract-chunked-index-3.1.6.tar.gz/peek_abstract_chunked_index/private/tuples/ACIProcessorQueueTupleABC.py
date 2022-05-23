from abc import abstractmethod


class ACIProcessorQueueTupleABC:
    @classmethod
    @abstractmethod
    def sqlCoreLoad(cls, row):
        """SQL Core - Load

        This method creates the declarative from an SQL core query.
        There is a lot of overhead from using the ORM to load this
        then expunging it. So instead an SQLCore query then create the tuple.

        Example code:

            return LiveDbRawValueQueueTuple(id=row.id,
                                            chunkKey=row.chunkKey,
                                            encodedData=row.encodedData,
                                            encodedHash=row.encodedHash,
                                            lastUpdate=row.lastUpdate)
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def ckiUniqueKey(self):
        """Chunked Index - Unique Key

        This method returns a unique key for this row item.

        Example code:

            return "%s:%s" % (self.modelSetId, self.key)
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def tupleType(cls):
        raise NotImplementedError()
