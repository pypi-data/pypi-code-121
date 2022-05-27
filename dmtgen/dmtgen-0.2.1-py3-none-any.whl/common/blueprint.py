from __future__ import annotations
from typing import Dict, Sequence
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .package import Package

from .blueprint_attribute import BlueprintAttribute


class Blueprint:
    """ " A basic SIMOS Blueprint"""

    def __init__(self, bp_dict: Dict, parent) -> None:
        self.parent = parent
        self.blueprint = bp_dict
        self.name = self.blueprint["name"]
        self.description = bp_dict.get("description","")
        self.__abstract = bp_dict.get("abstract",False)
        attributes = {}
        for a_dict in bp_dict.get("attributes",[]):
            attribute = BlueprintAttribute(a_dict)
            attributes[attribute.name]=attribute
        self.__attributes = attributes
        extends = bp_dict.get("extends",[])
        self.__extends = extends
        # We will resolve this later
        self.__extensions = None

    @property
    def name(self) -> str:
        """Entity id"""
        return self.__name

    @name.setter
    def name(self, value: str):
        """Set name"""
        self.__name = str(value)

    @property
    def description(self) -> str:
        """Entity id"""
        return self.__description

    @description.setter
    def description(self, value: str):
        """Set description"""
        self.__description = str(value)

    @property
    def abstract(self) -> bool:
        """If the blueprint represent an abstract type"""
        return self.__abstract

    @property
    def attributes(self) -> Sequence[BlueprintAttribute]:
        """Attributes"""
        return self.__attributes.values()

    @property
    def all_attributes(self) -> Dict[str,BlueprintAttribute]:
        """All combined attributes for the blueprint and its extensions"""
        # First we collect the extensions, since these may be overridden
        atributes = {}
        for extension in self.extensions:
            atributes.update(extension.all_attributes)
        # Then we add ours
        atributes.update(self.__attributes)
        return atributes



    @property
    def extensions(self) -> Sequence[Blueprint]:
        """Extensions"""
        if self.__extensions is not None:
            return self.__extensions

        self.__extensions =  [self.__resolve(extension) for extension in self.__extends]
        return self.__extensions

    def __resolve(self,extension: str):
        package: Package = self.parent
        return package.get_blueprint(extension)

    def get_path(self):
        """ Get full path to blueprint """
        parent = self.get_parent()
        if parent:
            return parent.get_path() + "/" + self.name
        # Then we are at root
        return "/" + self.name

    def get_parent(self) -> Package:
        return self.parent
