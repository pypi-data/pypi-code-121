"""Modules for handling model data flow."""
from abc import ABC
import importlib as _importlib
import inspect
import pkgutil
from typing import List

from bitfount.data import datasources
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasplitters import PercentageSplitter, SplitterDefinedInData
from bitfount.data.datastructure import DataStructure
from bitfount.data.exceptions import (
    BitfountSchemaError,
    DatabaseMissingTableError,
    DatabaseSchemaNotFoundError,
    DatabaseUnsupportedQueryError,
    DataNotLoadedError,
    DatasetSplitterError,
    DataStructureError,
    DuplicateColumnError,
)
from bitfount.data.helper import convert_epochs_to_steps
from bitfount.data.schema import BitfountSchema, TableSchema
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    DataPathModifiers,
    ImageRecord,
    SemanticType,
    TextRecord,
)
from bitfount.data.utils import DatabaseConnection

__all__: List[str] = [
    "BitfountSchema",
    "BitfountSchemaError",
    "CategoricalRecord",
    "ContinuousRecord",
    "DatabaseConnection",
    "DatabaseMissingTableError",
    "DatabaseSchemaNotFoundError",
    "DatabaseUnsupportedQueryError",
    "DatasetSplitterError",
    "DataNotLoadedError",
    "DataPathModifiers",
    "DataStructure",
    "DataStructureError",
    "DuplicateColumnError",
    "ImageRecord",
    "PercentageSplitter",
    "SemanticType",
    "SplitterDefinedInData",
    "TableSchema",
    "TextRecord",
    "convert_epochs_to_steps",
]

# import all concrete implementations of _BaseSource
# in the datasources/ directory
for _module_info in pkgutil.walk_packages(
    path=datasources.__path__,
    prefix=datasources.__name__ + ".",
):

    try:
        _module = _importlib.import_module(_module_info.name)
    except ImportError:
        pass
    finally:
        for _, cls in inspect.getmembers(_module, inspect.isclass):
            if issubclass(cls, _BaseSource) and ABC not in cls.__bases__:
                globals().update({cls.__name__: getattr(_module, cls.__name__)})
                __all__.append(cls.__name__)


# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
