__author__ = "hugo.inzirillo"

import json
from abc import abstractmethod, ABCMeta

from pandas import Timestamp


class AbstractModelParamTemplate(metaclass=ABCMeta):
    @property
    @abstractmethod
    def start_date(self):
        raise NotImplemented

    @property
    @abstractmethod
    def end_date(self):
        raise NotImplemented

    @property
    @abstractmethod
    def underlying(self):
        raise NotImplemented


class ModelParamTemplate(AbstractModelParamTemplate):
    def __init__(self):
        self.__start_date = None
        self.__end_date = None
        self.__underlyings = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return json.dumps(self.__dict__())

    def __dict__(self):
        return dict(start_date=self.__start_date,
                    end_date=self.__end_date,
                    underlyings=self.__underlyings)

    @property
    def start_date(self) -> Timestamp:
        return self.__start_date

    @property
    def end_date(self) -> Timestamp:
        return self.__end_date

    @property
    def underlying(self) -> dict:
        return self.__underlyings
