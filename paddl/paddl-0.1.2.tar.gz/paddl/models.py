from enum import Enum
from avro.schema import PrimitiveSchema


class ColType(Enum):
    STRING = "string"
    VARCHAR = "varchar"
    INT = 'int'


class Schema:
    """An analog for a database"""
    def __init__(self, name=None, description=None,
                 **kwargs):
        self.name = name
        self.description = description
        self.tables = [Table(**kw)
                       if isinstance(kw, dict) else kw
                       for kw in kwargs.get('tables', [])]


class Table:
    """A table or collection of records"""
    def __init__(self, name=None, columns=None, description='', **kwargs):
        if columns is None:
            columns = []

        self.name = name
        self.description = description
        self.columns = [Column(**col)
                        if isinstance(col, dict) else col
                        for col in columns]


class Column:
    """Atomic unit of data."""
    def __init__(self, name=None, type=None, description='', **kwargs):
        self.name = name
        self.description = description
        if isinstance(type, PrimitiveSchema):
            type = type.type
        self.type = ColType(type)
