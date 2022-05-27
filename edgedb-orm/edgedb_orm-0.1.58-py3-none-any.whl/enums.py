from enum import Enum


class PropertyCardinality(str, Enum):
    ONE = "ONE"
    MANY = "MANY"
