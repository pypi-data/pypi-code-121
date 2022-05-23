import logging
from abc import abstractmethod

logger = logging.getLogger(__name__)


class ACDLChunkLoadStateTupleABC:
    """Agent Import Chunk

    This table stores information used by the agent about when things need updating.
    There is no relation to the server objects, the agent can use this how ever it wants.

    The server never manipulates this table it's self.

    """

    @classmethod
    @abstractmethod
    def sqlCoreIdColumn(cls):
        """SQL Core - Chunk Key Column

        This method should return the SQL Core column

        :return: The column

        Example code:

                return cls.__table__.c.id

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

            return GraphSegmentLoadStateTuple(id=row.id,
                                            chunkKey=row.chunkKey,
                                            lastImportDate=row.lastImportDate,
                                            lastImportHash=row.lastImportHash)
        """
        raise NotImplementedError()
