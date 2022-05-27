"""Parsing functionaity for Transformation instances.

This module contains the transformations parser that will parse a set of
Transformation specifications from a YAML file and create a set of
Transformation instances.
"""
from collections import defaultdict
from os import PathLike
from typing import DefaultDict, Dict, Iterable, List, Mapping, Set, Tuple, Union, cast

import yaml

from bitfount.transformations.base_transformation import (
    TRANSFORMATION_REGISTRY,
    MultiColumnOutputTransformation,
    Transformation,
)
from bitfount.transformations.exceptions import TransformationParsingError
from bitfount.transformations.references import (
    _COLUMN_REFERENCE,
    _TRANSFORMATION_REFERENCE,
)


class TransformationsParser:
    """A parser for converting YAML configs into `Transformation` instances.

    :::info

    To refer to a column, we can use `c`, `col` or `column` as a prefix followed by the
    column name.

    To refer to a transformation, we can use `t`, `tran` or `transformation` as a prefix
    followed by the column name.

    :::
    """

    def parse(self, yaml_str: str) -> Tuple[List[Transformation], Set[str]]:
        """Parses a transformations YAML config into a list of Transformation objects.

        Args:
            yaml_str: The YAML config as a string.

        Returns: A tuple of the list of Transformation instances and any column names
            that are referenced.

        Raises:
            TransformationParserError: If parsing errors occur. The errors are stored on
                the `errors` attribute of the exception.
        """
        loaded = yaml.safe_load(yaml_str)
        return self.deserialize_transformations(loaded["Transformations"])

    def parse_file(
        self, path: Union[str, PathLike]
    ) -> Tuple[List[Transformation], Set[str]]:
        """Parses a transformations YAML file into a list of Transformation objects.

        Args:
            path: Path to the YAML config file.

        Returns: A tuple of the list of Transformation instances and any column names
            that are referenced.

        Raises:
            TransformationParserError: If parsing errors occur. The errors are stored on
                the `errors` attribute of the exception.
        """
        with open(path) as f:
            return self.parse(f.read())

    def deserialize_transformations(
        self, data: Iterable[Mapping[str, Mapping]]
    ) -> Tuple[List[Transformation], Set[str]]:
        """Deserializes a list of python objects into `Transformation` instances.

        Args:
            data: The serialized data representing the list of Transformations.

        Raises:
            TransformationParserError: If parsing errors occur. The errors are stored
                on the `errors` attribute of the exception.

        Returns:
            A tuple of the list of deserialized `Transformation` instances and any
            column names that are referenced.
        """
        transformations = []
        errors = []

        # Data should be a list/iterable of mappings of
        # transformation name -> transformation args
        for i, t_spec in enumerate(data):
            try:
                transformation = self._deserialize_transformation(i, t_spec)
                transformations.append(transformation)
            except TransformationParsingError as tpe:
                errors.extend(tpe.errors)

        # Check that each transformation has a unique name
        try:
            self._check_names_unique(transformations)
        except TransformationParsingError as tpe:
            errors.extend(tpe.errors)

        # Hook transformation references together, ensuring they are
        # correctly referenced
        try:
            self._hook_transformations_together(transformations)
        except TransformationParsingError as tpe:
            errors.extend(tpe.errors)

        # Extract the set of column names that are referenced
        col_refs = self._extract_column_refs(transformations)

        if errors:
            raise TransformationParsingError(errors)

        return transformations, col_refs

    def _deserialize_transformation(
        self, t_spec_idx: int, t_spec: Union[str, Mapping[str, Mapping]]
    ) -> Transformation:
        """Deserializes an individual transformation.

        Args:
            t_spec_idx:
                The index of the transformation spec in the list.
            t_spec:
                The mapping representing the transformation information.

        Raises:
            TransformationParserError:
                If the spec contains more than one mapping or if no transformation
                of that type is registered.

        Returns:
            The deserialized transformation.
        """
        # If t_spec isn't a key, convert it into one with no values
        if not isinstance(t_spec, Mapping):
            t_spec = {t_spec: {}}

        # Check that each mapping is only for a single transformation
        if len(t_spec) != 1:
            raise TransformationParsingError(
                f"Each transformation mapping must contain exactly one "
                f"transformation; mapping {t_spec_idx} contains {len(t_spec)}."
            )

        # Retrieve transformation schema from registry and deserialize
        t_name, t_details = list(t_spec.items())[0]  # as only one long
        t_name = t_name.lower()
        try:
            schema = TRANSFORMATION_REGISTRY[t_name].schema()
        except KeyError:
            raise TransformationParsingError(
                f"No transformation registered with name {t_name}."
            )
        transformation: Transformation = schema.load(t_details)
        return transformation

    def _check_names_unique(self, transformations: Iterable[Transformation]) -> None:
        """Checks that each transformation has a unique name.

        Args:
            transformations:
                List of transformation instances.

        Raises:
            TransformationParsingError:
                If duplicate names are detected.
        """
        errors = []
        seen = set()
        duplicated = set()
        multi_column_outputs = []

        for t in transformations:
            # Save multi-column output transformations to deal with their
            # additional columns later
            if isinstance(t, MultiColumnOutputTransformation):
                multi_column_outputs.append(t)

            # Check exact name conflicts
            name = t.name
            if name not in seen:
                seen.add(name)
            else:
                duplicated.add(name)
        if duplicated:
            errors.extend(
                [f"Duplicate transformation name: {dupe}." for dupe in duplicated]
            )

        # Check multi-column output transformations for clashes
        mco_clashes: DefaultDict[str, List[str]] = defaultdict(list)
        for t in multi_column_outputs:
            name = cast(str, t.name)
            cols = set(t.columns)

            # Find clashes against `seen` set.
            clashes = cols.intersection(seen)
            if clashes:
                mco_clashes[name].extend(clashes)
            # Regardless, need to update `seen` with the new cols
            seen.update(cols)
        if mco_clashes:
            errors.extend(
                [
                    f"Multi-column output clash: {clash} "
                    f"(from output column of {name})."
                    for name, clashes in mco_clashes.items()
                    for clash in clashes
                ]
            )

        # Raise any errors that occur
        if errors:
            raise TransformationParsingError(errors)

    def _hook_transformations_together(
        self, transformations: Iterable[Transformation]
    ) -> None:
        """Replaces transformation name references with the actual transformations.

        Iterates through all Transformations, replacing any arguments that reference
        other Transformations by name with the actual Transformations.

        Args:
            transformations:
                The list of transformations.

        Raises:
            TransformationParsingError:
                If references are made to transformations that have yet to be defined
                in the order.
        """
        errors = []
        transforms_map: Dict[str, Transformation] = dict()

        # In order, check that any references to previous transformations are
        # correct and exist.
        for t in transformations:
            t.name = cast(str, t.name)
            transforms_map[t.name] = t

            # Check if any attributes reference transformations
            for attr, value in vars(t).items():
                try:
                    match = _TRANSFORMATION_REFERENCE.fullmatch(value)
                    # If referencing a transformation, replace the attribute with
                    # the actual transformation instance. Raise exception if the
                    # transformation hasn't been seen yet.
                    if match:
                        ref = match.group(1)
                        try:
                            setattr(t, attr, transforms_map[ref])
                        except KeyError:
                            errors.append(
                                f"Transformation, {t.name}, attempted to use "
                                f'transformation "{ref}" before it was defined.'
                            )
                except TypeError:
                    pass

        if errors:
            raise TransformationParsingError(errors)

    def _extract_column_refs(
        self, transformations: Iterable[Transformation]
    ) -> Set[str]:
        """Extracts the names of any columns referenced in the transformations.

        Args:
            transformations:
                The list of transformations.

        Returns:
            The set of column names referenced in transformation attributes.
        """
        col_refs = set()

        def add_col_ref(string: str) -> None:
            match = _COLUMN_REFERENCE.fullmatch(string)
            if match:
                col_refs.add(match.group(1))

        for t in transformations:
            for _attr, value in vars(t).items():
                try:
                    if isinstance(value, list):
                        for value_ in value:
                            add_col_ref(value_)
                    else:
                        add_col_ref(value)
                except TypeError:
                    pass
        return col_refs
