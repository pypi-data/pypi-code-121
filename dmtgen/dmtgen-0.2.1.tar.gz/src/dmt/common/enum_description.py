from __future__ import annotations
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from .package import Package



class EnumDescription:
    """ " A basic DMT Enum"""

    def __init__(self, enum_dict: Dict, parent) -> None:
        self.parent = parent
        self.blueprint = enum_dict
        self.name = self.blueprint["name"]
        self.description = enum_dict.get("description","")
        values = enum_dict["values"]
        labels = enum_dict["labels"]
        self.enum_values = []
        self.default = values[0]
        for i, value in enumerate(values):
            self.enum_values.append({
                "value": value,
                "label": labels[i]
            })

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

    def get_path(self):
        """ Get full path to blueprint """
        parent = self.get_parent()
        if parent:
            return parent.get_path() + "/" + self.name
        # Then we are at root
        return "/" + self.name

    def get_parent(self) -> Package:
        return self.parent
