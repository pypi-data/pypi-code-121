""" " A basic SIMOS package"""


from __future__ import annotations
import json

import re
from pathlib import Path
from typing import List, Sequence

from .enum_description import EnumDescription
from .blueprint import Blueprint

class Package:
    """ " A basic SIMOS package"""

    def __init__(self, pkg_dir: Path) -> None:
        self.version = 0
        self.__read_package(pkg_dir)

    def __read_package(self, pkg_dir: Path):
        self.parent = None
        blueprints = {}
        enums = {}
        self.__blueprints = blueprints
        self.__enums = enums
        self.__packages = {}
        self.name = pkg_dir.name

        for file in pkg_dir.glob("*.json"):
            entity = json.load(open(file, encoding="utf-8"))
            if file.name == "__versions__.json":
                self.__read_version(entity)
            else:
                etype = entity["type"]
                if etype == "system/SIMOS/Blueprint":
                    blueprint = Blueprint(entity, self)
                    name = blueprint.name
                    blueprints[name] = blueprint
                elif etype == "system/SIMOS/Enum":
                    enum = EnumDescription(entity, self)
                    name = enum.name
                    enums[name] = enum
                else:
                    raise Exception("Unhandled entity type: " + etype)

        for folder in pkg_dir.glob("*/"):
            if folder.is_dir():
                sub_package = Package(folder)
                sub_package.parent = self
                self.__packages[sub_package.name] = sub_package

    def __read_version(self,versions: dict):
        self.version = versions.get(self.name,None)

    def get_path(self) -> str:
        """ Get full type path to package """
        parent = self.get_parent()
        if parent:
            return parent.get_path() + "/" + self.name
        # Then we are root
        return self.name

    def get_paths(self) -> List[str]:
        """ Get full type path to package """
        parent = self.get_parent()
        if parent:
            parent_paths = parent.get_paths()
            parent_paths.append(self.name)
            return parent_paths
        # Then we are root
        return [self.name]

    @property
    def blueprints(self) -> Sequence[Blueprint]:
        return self.__blueprints.values()

    @property
    def enums(self) -> Sequence[EnumDescription]:
        return self.__enums.values()

    def blueprint(self, name:str) -> Blueprint:
        bp = self.__blueprints.get(name,None)
        if not bp:
            raise Exception(f"Blueprint not found \"{name}\" in {self.name}")
        return bp

    def enum(self, name:str) -> EnumDescription:
        enum = self.__enums.get(name,None)
        if not enum:
            raise Exception(f"Enum not found \"{name}\" in {self.name}")
        return enum


    @property
    def packages(self) -> Sequence[Package]:
        """Attributes"""
        return self.__packages.values()

    def package(self, name:str) -> Package:
        """Attributes"""
        pkg = self.__packages.get(name,None)
        if not pkg:
            raise Exception(f"package not found \"{name}\" in {self.name}")
        return pkg

    def get_parent(self) -> Package:
        return self.parent

    def get_root(self):
        parent: Package = self.parent
        if parent:
            return parent.get_root()
        # No parent so we are root
        return self


    def get_blueprint(self, path:str) -> Blueprint:
        parts = re.split("/",path)
        bp_name = parts.pop()
        package = self.__get_package(parts)
        return package.blueprint(bp_name)

    def get_enum(self, path:str) -> EnumDescription:
        parts = re.split("/",path)
        enum_name = parts.pop()
        package = self.__get_package(parts)
        return package.enum(enum_name)

    def __get_package(self, parts: Sequence[str]) -> Package:
        package: Package = None
        for part in parts:
            if part == '':
                package = self.get_root()
            elif part == 'system':
                from .system_package import system_package
                package =  system_package
            elif package is None:
                package = self.get_root()
                if part != package.name:
                    raise Exception(f"expected root {package.name} but got {part}")
            else:
                package = package.package(part)
        return package
