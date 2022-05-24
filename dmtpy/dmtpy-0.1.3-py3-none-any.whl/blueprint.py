"""
Blueprint with attributes
"""
from typing import Iterator, List
from .blueprint_attribute import BlueprintAttribute
from .dimension import Dimension
from .attribute import Attribute


class Blueprint:
    """The Entity metadata"""

    def __init__(self, name: str, package_path: str, description: str = None) -> None:
        self.name = name
        self.package_path = package_path
        self.version = 1
        self.description = description
        self.attributes: List[Attribute] = list()
        self.dimensions: List[Dimension] = list()

    def get_path(self):
        """Full path to this type"""
        return self.package_path + "/" + self.name

    def get_attribute(self, name: str) -> Attribute:
        """Get attribute of given name"""
        for prop in self.attributes:
            if prop.name == name:
                return prop
        return None

    def get_dimension(self, name: str) -> Dimension:
        """Get dimension by name"""
        for dim in self.dimensions:
            if dim.name == name:
                return dim
        return None

    def blueprint_attributes(self) -> Iterator[BlueprintAttribute]:
        """Get all blueprint attributes"""
        for p in self.attributes:
            if isinstance(p, BlueprintAttribute):
                yield p
