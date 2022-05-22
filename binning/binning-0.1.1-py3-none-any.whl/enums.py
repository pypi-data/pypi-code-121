from enum import Enum, unique


@unique
class Distribution(Enum):
    DISCRETE = 0
    CONTINUOUS = 1


@unique
class BinType(Enum):
    DISTANCE_BIN = "distanceBin"
    FREQUENCY_BIN = "frequencyBin"
    ENUMERATE_BIN = "enumerateBin"
    CUSTOM_BIN = "customBin"
    CHIMERGE_BIN = "chimergeBin"


@unique
class CalType(Enum):
    WOEIV = "woeiv"
