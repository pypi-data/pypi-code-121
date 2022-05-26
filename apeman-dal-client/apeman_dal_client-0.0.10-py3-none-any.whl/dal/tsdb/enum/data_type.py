from enum import Enum


class DataType(Enum):
    UNKNOWN = 'UNKNOWN'
    TEXT = 'TEXT'
    UUID = 'UUID'
    TIMESTAMP = 'TIMESTAMP'
    BIGINT = 'BIGINT'
    BOOLEAN = 'BOOLEAN'
    DOUBLE = 'DOUBLE'
