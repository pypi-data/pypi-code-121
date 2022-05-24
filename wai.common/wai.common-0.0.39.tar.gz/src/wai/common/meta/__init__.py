"""
Package for meta-programming constructs.
"""
from ._fully_qualified_name import fully_qualified_name
from ._functions import (
    has_been_overridden,
    get_class_from_function,
    is_class_function,
    unbind,
    does_not_raise,
    all_as_kwargs
)
from ._import_code import get_import_code
from ._instanceoptionalmethod import instanceoptionalmethod
from ._InstanceProperty import InstanceProperty
from ._metadata import with_metadata, get_metadata, has_metadata
from ._non_default_kwargs import non_default_kwargs
