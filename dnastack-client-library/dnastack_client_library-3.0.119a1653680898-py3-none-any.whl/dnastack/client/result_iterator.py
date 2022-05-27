from logging import Logger
from uuid import uuid4

from abc import ABC
from threading import Lock
from typing import Any, Dict, List, Optional

from dnastack.common.logger import get_logger


class ResultLoader(ABC):
    __uuid__: Optional[str] = None
    __logger__: Optional[Logger] = None

    @property
    def uuid(self):
        if not self.__uuid__:
            self.__uuid__ = str(uuid4())
        return self.__uuid__

    @property
    def logger(self):
        if not self.__logger__:
            self.__logger__ = get_logger(f'{type(self).__name__}/{self.uuid}')
        return self.__logger__

    def load(self) -> List[Dict[str, Any]]:
        ...

    def has_more(self) -> bool:
        ...


class ResultIterator:
    def __init__(self, loader: ResultLoader):
        self.__read_lock = Lock()
        self.__loader = loader
        self.__buffer: List[Dict[str, Any]] = []
        self.__depleted = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.__depleted:
            self.__loader.close()
            raise StopIteration('Already depleted')

        with self.__read_lock:
            while not self.__buffer:
                # Refill the buffer
                if not self.__buffer and not self.__depleted:
                    if self.__loader.has_more():
                        try:
                            self.__buffer.extend(self.__loader.load())
                        except StopIteration as e:
                            self.__depleted = True
                            raise e
                    else:
                        self.__depleted = True
                        raise StopIteration('No more result to iterate')

            # Read within the lock
            item = self.__buffer.pop(0)

        return item
