from enum import Enum


class Types(Enum):
    String = str
    Int = int
    Float = float
    Bool = bool
    List = list
    Dict = dict


class MetaTypes(Enum):
    String = 1
    Pairs = 2


