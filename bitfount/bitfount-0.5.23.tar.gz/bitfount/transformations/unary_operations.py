"""Unary (one reference argument) transformations.

This module contains the base class and concrete classes for unary transformations,
those that take a single reference argument (i.e. a column or transformation name).
"""
from __future__ import annotations

import copy
from functools import cached_property
import logging
from typing import Any, Dict, List, Optional, Union, cast

import attr
from marshmallow import fields, post_load
import marshmallow_union

from bitfount.transformations.base_transformation import (
    MultiColumnOutputTransformation,
    Transformation,
    _TransformationSchema,
)
from bitfount.transformations.exceptions import IncorrectReferenceError
from bitfount.transformations.references import _extract_ref
from bitfount.types import _JSONDict


@attr.dataclass(kw_only=True)
class UnaryOperation(Transformation):
    """The base abstract class for all Unary Operation Transformations.

    Args:
        arg: The argument to the transformation.
    """

    arg: Any


@attr.dataclass(kw_only=True)
class StringUnaryOperation(UnaryOperation):
    """This class represents any UnaryOperation where arg can only be a string.

    Args:
        arg: The argument to the transformation as a string.
    """

    arg: str


@attr.dataclass(kw_only=True)
class OneHotEncodingTransformation(
    StringUnaryOperation, MultiColumnOutputTransformation
):
    """One hot encoding transformation.

    Represents the transformation of a column into a series of one-hot encoded
    columns.

    Attributes:
        arg: Column or transformation reference to one-hot encode.
        values: Column values that should be one-hot encoded. This can either be
            a list of values, in which case the one-hot encoding will produce
            columns named `{name}_{value}`, or a dictionary of values to desired
            column suffixes, in which case the encoding will use those suffixes
            (if an entry in the dictionary maps to None, the column name will be
            generated in the same way as described above).

            If `name` is not set, the column or transformation reference from
            `arg` will be used instead.

            Any value found in the column which is not enumerated in this argument
            will be encoded in an `{name}_{unknown_suffix}` column. This column is
            therefore protected and any value or value-column mapping that could
            clash will raise ValueError. If you need to encode such a value,
            `unknown_suffix` must be changed
        unknown_suffix: The suffix to use to create a column for encoding unknown
            values. The column will be created as `{name}_{unknown_suffix}`.
            Default is "UNKNOWN".

    Raises:
        ValueError: If any name in `values` would cause a clash with the unknown
            value column created by `unknown_suffix` or with another generated column.
        ValueError: If no `values` were provided.
        ValueError: If no name is provided and the reference in arg cannot be found.
    """

    _registry_name = "onehotencode"

    values: Dict[Any, str] = attr.ib(init=False, default=None)
    unknown_suffix: str = "UNKNOWN"

    # This is used as a temporary placeholder for the values
    _raw_values: Union[List[Any], Dict[Any, Optional[str]]]
    # This is used to mark if name was set or not
    _no_name_provided: bool = attr.ib(init=False, default=False)

    def __attrs_post_init__(self) -> None:
        # Set this first as the super() call will randomly init name if not set
        if not self.name:
            self._no_name_provided = True
        super().__attrs_post_init__()

        # Check at least one value provided
        if len(self._raw_values) == 0:
            raise ValueError("At least one value must be provided to one-hot encode.")

        self._produce_full_col_map()

    @property
    def columns(self) -> List[str]:
        """Lists the columns that will be output."""
        return list(self.values.values()) + [self.unknown_col]

    @cached_property
    def prefix(self) -> str:
        """Uses name as prefix or extract from arg (should be col or transform ref)."""
        # If name has been randomly set, try to use arg reference instead.
        # If arg isn't a reference, we have to fail out.
        if self._no_name_provided:
            try:
                return _extract_ref(self.arg)
            except IncorrectReferenceError as ire:
                raise ValueError(
                    "No name provided and no reference found in arg."
                ) from ire
        # If name is provided, use it
        else:
            return cast(str, self.name)

    @property
    def unknown_col(self) -> str:
        """Returns the name of the column that unknown values are encoded to."""
        return f"{self.prefix}_{self.unknown_suffix}"

    def _produce_full_col_map(self) -> None:
        """Takes loaded values and produces full value-column map.

        Validates that the values will give unique column names.
        """
        # If self.values already exists, don't redo
        if cast(Optional[Dict[Any, str]], self.values) is not None:
            logging.warning("_produce_full_col_map should not be called more than once")
            return

        prefix = self.prefix

        # Convert list to dict format (provide null mappings for now)
        tmp_values_w_null: Dict[Any, Optional[str]]
        if isinstance(self._raw_values, list):
            tmp_values_w_null = {i: None for i in self._raw_values}
            # Check for duplicate values at this point
            if len(self._raw_values) != len(tmp_values_w_null):
                raise ValueError("If `raw_values` is a list, elements must be unique.")
        else:  # if _raw_values is a dict, copy
            tmp_values_w_null = copy.deepcopy(self._raw_values)

        # Generate column names
        for ohe_val, col_suffix in tmp_values_w_null.items():
            # Use suffix if provided
            if col_suffix:
                col_name = f"{prefix}_{col_suffix}"
            # Otherwise use ohe_val
            else:
                col_name = f"{prefix}_{str(ohe_val)}"
            tmp_values_w_null[ohe_val] = col_name

        # All entries have str values at this point
        tmp_values: Dict[Any, str] = cast(Dict[Any, str], tmp_values_w_null)

        # Check column names are unique
        col_names = tmp_values.values()
        if len(col_names) != len(set(col_names)):
            raise ValueError(
                f"Column names generated must be unique: {sorted(col_names)}"
            )

        # Check each potential column name against the unknown column
        unknown_col = self.unknown_col
        if any(unknown_col == col_name for col_name in col_names):
            raise ValueError(
                f"At least one column name clashes with the unknown value "
                f"column: {unknown_col}"
            )

        # Set self.values to calculated version
        self.values = tmp_values

    class _Schema(_TransformationSchema):
        # From Transformation
        name = fields.String(default=None)
        output = fields.Boolean(default=False)
        # From StringUnaryOperation
        arg = fields.String(required=True)
        # From OneHotEncodingTransformation
        values = marshmallow_union.Union(
            [
                fields.List(fields.Raw),
                fields.Dict(keys=fields.Raw, values=fields.String(allow_none=True)),
            ],
            required=True,
        )
        unknown_suffix = fields.String(default="UNKNOWN")

        @post_load
        def make_transformation(
            self, data: _JSONDict, **_kwargs: Any
        ) -> OneHotEncodingTransformation:
            """Makes a OneHotEncodingTransformation from the schema."""
            # Need to move schema "values" to "raw_values" for __init__ call.
            # It's not "_raw_values" because of how attrs handles private variables.
            raw_values = data.pop("values")
            data["raw_values"] = raw_values
            return OneHotEncodingTransformation(**data)


@attr.dataclass(kw_only=True)
class InclusionTransformation(StringUnaryOperation):
    """Represents the test for substring inclusion in a column's entries.

    Check whether `in_str` (the test string) is in the elements of `arg` (the column).

    Args:
        in_str: The string to test for inclusion.
    """

    _registry_name = "in"

    in_str: str
