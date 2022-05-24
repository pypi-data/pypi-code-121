"""
Package for working with code-representations of objects.
"""
from ._CodeRepresentable import CodeRepresentable
from ._error import CodeRepresentationError, IsNotCodeRepresentableValue, IsNotCodeRepresentableType, ConflictingImports
from ._functional import code_repr, get_code_repr_function
from ._typing import ImportDict, CodeRepresentation, CodeReprFunction
from ._utilities import combine_import_dicts, from_init, get_code, get_import_dict
