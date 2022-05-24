"""
{"name": "x", "type": "float", "description": "point, x coordinates"},
"""
from .attribute import Attribute

class EnumAttribute(Attribute):
    """ An Enum attribute"""

    def __init__(self,name:str ,attribute_type:str,description:str) -> None:
        super().__init__(name,attribute_type,description)

    @property
    def contained(self) -> bool:
        return False

    @property
    def is_primitive(self) -> bool:
        """Is this a primitive attribute"""
        return False

    @property
    def is_enum(self) -> bool:
        return True
