import dataclasses
import logging
from abc import ABC
from dataclasses import dataclass
from lib2to3.pytree import Base

from cleandev_validator.inmutables import _DataClassConstrains



class DataClass(ABC):

    def _validate(self, **kwargs):
        self.__dict__.update(kwargs)
        for field in self.__fields__:

            if field in dict(self.__constrains__):
                constraint = str(dict(self.__constrains__)[field])

                if constraint == str(_DataClassConstrains.BOOL):
                    self.__validate_bool(field)

                if constraint == str(_DataClassConstrains.STR):
                    self.__validate_str(field)

                if constraint == str(_DataClassConstrains.INT):
                    self.__validate_int(field)

    def __validate_bool(self, field):
        if not isinstance(getattr(self, field), bool):
            logging.exception(f" El tipo de la variable {field} no es del tipo 'BOOL'")
            exit()

    def __validate_int(self, field):
        if not isinstance(getattr(self, field), int):
            logging.exception(f" El tipo de la variable {field} no es del tipo 'INT'")
            exit()

    def __validate_str(self, field):
        if not isinstance(getattr(self, field), str):
            logging.exception(f" El tipo de la variable {field} no es del tipo 'STR'")
            exit()


    @property
    def __fields__(self):
        return list(self.__annotations__.keys())

    def __filter__(self, items: list, include: bool = True):
        data = self.__dict__
        if include:
            return dict(filter(lambda entry: entry[0] in items, data.items()))
        return dict(filter(lambda entry: entry[0] not in items, data.items()))
