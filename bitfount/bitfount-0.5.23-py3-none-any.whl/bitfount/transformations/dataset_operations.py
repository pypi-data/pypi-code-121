"""Dataset-related transformations.

This module contains the base class and concrete classes for dataset transformations,
those that potentially act over the entire dataset.
"""
from typing import List, Mapping, Union

import attr

from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.exceptions import TransformationApplicationError


@attr.dataclass(kw_only=True)
class DatasetTransformation(Transformation):
    """Base transformation for all dataset transformation classes.

    User can specify "all" to have it act on every relevant column as defined
    in the schema.

    Args:
        output: Whether or not this transformation should be included in the final
            output. This must be True for all dataset transformations. Defaults to True.
        cols: The columns to act on as a list of strings. Defaults to "all" which acts
            on all columns in the dataset.

    Raises:
        ValueError: If `output` is False.
    """

    output: bool = True
    cols: Union[str, List[str]] = "all"

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not self.output:
            raise ValueError("`output` cannot be False for a DatasetTransformation")


@attr.dataclass(kw_only=True)
class CleanDataTransformation(DatasetTransformation):
    """Dataset transformation that will "clean" the specified columns.

    For continuous columns this will replace all infinities and NaNs with 0.
    For categorical columns this will replace all NaN's with "nan" explicitly.
    """

    _registry_name = "cleandata"


@attr.dataclass(kw_only=True)
class NormalizeDataTransformation(DatasetTransformation):
    """Dataset transformation that will normalise the specified continuous columns.

    Args:
        cols: The columns to act on as a list of strings. By default, this
            transformation will only apply to columns of type float.

    If this transformation should be applied to all continuous columns,
    the cols attribute should be set to 'all'.
    """

    cols: Union[str, List[str]] = "float"
    _registry_name = "normalizedata"


@attr.dataclass(kw_only=True)
class ScalarMultiplicationDataTransformation(DatasetTransformation):
    """Dataset transformation that multiplies the specified columns by a scalar.

    Transformation applied to the dataset in place. Only applies to continuous columns.

    Args:
        scalar: the scalar to be used for multiplication. It can be provided
            as a number, in which case all numerical columns will be multiplied
            by the respective scalar or as a dictionary mapping column names
            to scalars for multiplication. Defaults to 1.

    Raises:
        TransformationApplicationError: if the scalar variable is not correctly
                instantiated.
    """

    scalar: Union[int, float, Mapping[str, Union[int, float]]] = 1
    _registry_name = "scalarmultiply"

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.scalar, (int, float, dict)):
            raise TransformationApplicationError(
                f"The scalar definition ({self.scalar}) for this transformation is"
                " incorrect. Please make sure you pass an integer, a float, or a"
                " dictionary with column names mapped to the value of the scalar"
                " that the respective column should be mapped to."
            )


@attr.dataclass(kw_only=True)
class ScalarAdditionDataTransformation(DatasetTransformation):
    """Dataset transformation that adds a scalar to the specified columns.

    Transformation applied to the dataset in place. Only applies to continuous columns.

    Args:
        scalar: the scalar to be used for multiplication. It can be provided
            as a number, in which case all numerical columns will be multiplied
            by the respective scalar or as a dictionary mapping column names
            to scalars for multiplication. Defaults to 0.

    Raises:
        TransformationApplicationError: if the scalar variable is not correctly
                instantiated.
    """

    scalar: Union[int, float, Mapping[str, Union[int, float]]] = 0
    _registry_name = "scalaradd"

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.scalar, (int, float, dict)):
            raise TransformationApplicationError(
                f"The scalar definition ({self.scalar}) for this transformation is"
                " incorrect. Please make sure you pass an integer, a float, or a"
                " dictionary with column names mapped to the value of the scalar"
                " that the respective column should be mapped to."
            )
