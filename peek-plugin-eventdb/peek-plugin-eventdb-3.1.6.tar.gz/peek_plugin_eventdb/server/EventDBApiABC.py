from abc import ABCMeta, abstractmethod

from peek_plugin_eventdb.server.EventDBReadApiABC import EventDBReadApiABC
from peek_plugin_eventdb.server.EventDBWriteApiABC import EventDBWriteApiABC


class EventDBApiABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def writeApi(self) -> EventDBWriteApiABC:
        """EventDB Write API

        This API is for all the methods that make changes to the EventDB

        :return: A reference to the EventDBWriteApiABC instance

        """

    @property
    @abstractmethod
    def readApi(self) -> EventDBReadApiABC:
        """EventDB Read API

        This API is for all the methods to read changes from the EventDB

        :return: A reference to the EventDBReadApiABC instance

        """
