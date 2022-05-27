"""Modules related to the transformations framework.

All transformations should be imported here so that they are automatically added to the
transformations registry.
"""
from typing import List

from bitfount.transformations.batch_operations import (
    IMAGE_TRANSFORMATIONS,
    ImageTransformation,
)
from bitfount.transformations.binary_operations import (
    AdditionTransformation,
    ComparisonTransformation,
    DivisionTransformation,
    MultiplicationTransformation,
    SubtractionTransformation,
)
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    NormalizeDataTransformation,
)
from bitfount.transformations.exceptions import (
    IncorrectReferenceError,
    InvalidBatchTransformationError,
    MissingColumnReferenceError,
    NotColumnReferenceError,
    NotTransformationReferenceError,
    TransformationApplicationError,
    TransformationParsingError,
    TransformationProcessorError,
    TransformationRegistryError,
)
from bitfount.transformations.parser import TransformationsParser
from bitfount.transformations.processor import TransformationProcessor
from bitfount.transformations.unary_operations import (
    InclusionTransformation,
    OneHotEncodingTransformation,
)

__all__: List[str] = [
    "AdditionTransformation",
    "CleanDataTransformation",
    "ComparisonTransformation",
    "DivisionTransformation",
    "IMAGE_TRANSFORMATIONS",
    "ImageTransformation",
    "InclusionTransformation",
    "IncorrectReferenceError",
    "InvalidBatchTransformationError",
    "MissingColumnReferenceError",
    "MultiplicationTransformation",
    "NormalizeDataTransformation",
    "NotColumnReferenceError",
    "NotTransformationReferenceError",
    "OneHotEncodingTransformation",
    "SubtractionTransformation",
    "TransformationApplicationError",
    "TransformationsParser",
    "TransformationParsingError",
    "TransformationProcessor",
    "TransformationProcessorError",
    "TransformationRegistryError",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
