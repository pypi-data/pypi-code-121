import enum


class Endianness(str, enum.Enum):
    LITTLE = "LITTLE"
    BIG = "BIG"
