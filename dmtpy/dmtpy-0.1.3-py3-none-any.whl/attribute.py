"""
{"name": "x", "type": "float", "description": "point, x coordinates"},
"""
from .dimension import Dimension

class Attribute:
    """ An attribute"""

    def __init__(self,name:str ,attribute_type:str,description:str, *dimensions: Dimension,
                 optional=True, default=None) -> None:
        self.name = name
        self.__type = attribute_type
        self.description = description
        self.dimensions = dimensions
        self.optional = optional
        self.default = default

    def has_dimensions(self):
        """Has dimensions"""
        return self.dimensions and len(self.dimensions)>0

    def is_boolean(self):
        """Is this a boolean primitive?"""
        return self.__type == 'boolean'

    def is_string(self):
        """Is this a String primitive?"""
        return self.__type == 'string' or self.__type == 'char'

    @property
    def contained(self) -> bool:
        """Is this attribute contained"""
        return True

    @property
    def is_primitive(self) -> bool:
        """Is this a primitive attribute"""
        return True

    @property
    def type(self) -> str:
        return self.__type

    @property
    def is_enum(self) -> bool:
        """Is this an enum primitive?"""
        return False
