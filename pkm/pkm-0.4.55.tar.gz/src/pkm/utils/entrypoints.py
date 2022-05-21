from __future__ import annotations

import re
from dataclasses import dataclass
from functools import reduce
from importlib import import_module
from types import ModuleType
from typing import ClassVar, Optional, List, Any

from pkm.api.packages.package import PackageDescriptor
from pkm.utils.commons import UnsupportedOperationException

# noinspection RegExpRedundantEscape
_OBJ_REF_RX = re.compile(r"(?P<mdl>[^:]*)(:(?P<obj>[^\[]*)\s*(\[\s*(?P<ext>[^\]]*)\s*\])?)?")
_EXT_DELIM_RX = re.compile("\\s*,\\s*")


@dataclass(frozen=True)
class ObjectReference:
    """
    The object reference points to a Python object. It is either in the form importable.module,
    or importable.module:object.attr.
    Each of the parts delimited by dots and the colon is a valid Python identifier.

    read more about it here: https://packaging.python.org/en/latest/specifications/entry-points/
    """
    module_path: str
    object_path: Optional[str] = None
    extras: Optional[List[str]] = None

    def __str__(self):
        obj_str = f":{self.object_path}" if self.object_path else ""
        ext_str = f" [{', '.join(self.extras)}]" if self.extras else ""
        return f"{self.module_path}{obj_str}{ext_str}"

    def import_module(self) -> ModuleType:
        return import_module(self.module_path)

    def import_object(self) -> Any:
        module = self.import_module()
        return reduce(getattr, self.object_path.split("."), module)

    def execution_script_snippet(self) -> str:
        if not self.object_path:
            raise UnsupportedOperationException(
                f"{str(self)} cannot be used as script generator - "
                f"it must be of the format module.path:zero.arg.function.path")

        return f"import sys;import {self.module_path};sys.exit({self.module_path}.{self.object_path}())"

    @classmethod
    def parse(cls, refstr: str) -> "ObjectReference":
        if not (match := _OBJ_REF_RX.match(refstr)):
            raise ValueError(f"could not parse object reference from string: '{refstr}'")

        module_path = match.group('mdl')
        object_path = match.group('obj')
        extras = _EXT_DELIM_RX.split(ext.strip()) if (ext := match.group('ext')) else None

        return ObjectReference(module_path, object_path, extras)


@dataclass
class EntryPoint:
    """
    Entry points are a mechanism for an installed distribution to advertise components it provides to be discovered and
    used by other code.
    read more about it here: https://packaging.python.org/en/latest/specifications/entry-points/
    """

    group: str
    name: str
    ref: "ObjectReference"
    containing_package: Optional[PackageDescriptor] = None

    G_CONSOLE_SCRIPTS: ClassVar[str] = "console_scripts"
    G_GUI_SCRIPTS: ClassVar[str] = "gui_scripts"

    def is_script(self) -> bool:
        """
        :return: true if this entrypoint belongs to one of the script groups, false otherwise
        """

        return self.group in (EntryPoint.G_CONSOLE_SCRIPTS, EntryPoint.G_GUI_SCRIPTS)
