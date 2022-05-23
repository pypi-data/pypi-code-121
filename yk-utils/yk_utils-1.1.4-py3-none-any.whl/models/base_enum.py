""" Base enum
"""
from enum import Enum
from typing import TypeVar, List

GenericVariable = TypeVar('T')


class BaseEnum(Enum):
    """
    Base enumerables with reusable methods
    """
    @classmethod
    def from_str(cls, value: str) -> 'BaseEnum':
        """
        convert from str to enumerable
        :param value:
            input string.
        :return:
            Derived type from BaseEnum
        :raises:
            ValueError if enum is invalid.
        """
        if value is None or value not in cls.__dict__:
            raise ValueError('Invalid enum type')
        return cls.__dict__[value]

    @classmethod
    def from_dict(cls, input_str: List[str]) -> List['BaseEnum']:
        """
        :param input_str:
            List of string with enums
        :return:
            List['BaseEnum']
        :raises:
            ValueError if provided processing is not available.
        """
        output_enums = None
        if input_str is not None:
            for processing in input_str:
                if output_enums is None:
                    output_enums = []
                if processing not in cls.__dict__:
                    raise ValueError("Enum not supported.")
                output_enums.append(cls.__dict__[processing])

        return output_enums

    @classmethod
    def to_dict_list(cls, input_enums: List['BaseEnum']) -> List[str]:
        """
        :param input_enums:
            List of BaseEnums
        :return:
            List[str]
        """
        outputs = None
        if input_enums is not None:
            for input_enum in input_enums:
                if outputs is None:
                    outputs = []
                outputs.append(input_enum.name)
        return outputs

    def to_dict(self) -> str:
        """
        Used to serialize a enum to string for jsons.
        :return:
            String name of enumerable
        """
        return self.name

    @classmethod
    def from_str_list(cls, input_enums: List[str]) -> List['BaseEnum']:
        """
        :param input_enums:
            Input to be convert to list of BaseEnum:
        :return:
            List of BaseEnum
        """
        outputs = None
        if input_enums is not None:
            outputs = []
            for input_e in input_enums:
                if input_e not in cls.__dict__:
                    raise ValueError("Enum not available.")
                outputs.append(cls.__dict__[input_e])
        return outputs

    @classmethod
    def to_str_list(cls) -> List['str']:
        """
        :return:
            List of str
        """
        return list(map(lambda c: c.name, cls))
