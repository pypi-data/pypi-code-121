"""Tests for dataset transformations."""
from typing import Type

from marshmallow import ValidationError
import pytest

from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    DatasetTransformation,
    NormalizeDataTransformation,
)
from tests.bitfount.transformations.transformation_test_helpers import (
    gen_name_fails,
    gen_name_test,
    registration_test,
)
from tests.utils.helper import unit_test


@unit_test
class TestDatasetTransformation:
    """Tests for the DatasetTransformation abstract transformation."""

    def test__gen_name_fails(self) -> None:
        """Tests that name generation fails."""
        gen_name_fails(DatasetTransformation)

    def test_schema_loads(self) -> None:
        """Tests schema load works correctly."""
        s = DatasetTransformation.schema()
        t = s.loads(
            """
            name: test
            output: True
            cols: col:A
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.cols == "col:A"

    def test_schema_loads_default_args(self) -> None:
        """Tests the state of the default args on schema load."""
        s = DatasetTransformation.schema()
        t = s.loads(
            """
            name: test
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.cols == "all"

    def test_schema_loads_false_output(self) -> None:
        """Tests schema load fails if output is False."""
        s = DatasetTransformation.schema()
        with pytest.raises(ValueError):
            s.loads(
                """
                name: test
                output: False
                """
            )

    def test_schema_load_fails_cols_nonstring(self) -> None:
        """Tests schema load fails if cols argument is not a string."""
        s = DatasetTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                cols: 1
                """
            )


def gen_name_test_dataset(cls: Type[Transformation], registry_name: str) -> None:
    """Tests name generation for dataset transformation classes.

    Test that a dataset transformation class is created with the correctly generated
    random name.
    """
    gen_name_test(cls, registry_name, cols="cols:A")


@unit_test
class TestCleanDataTransformation:
    """Tests for CleanDataTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_dataset(CleanDataTransformation, "cleandata")

    def test_registration(self) -> None:
        """Tests transformations registration."""
        registration_test(CleanDataTransformation, "cleandata")


@unit_test
class TestNormalizeDataTransformation:
    """Tests for NormalizeDataTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_dataset(NormalizeDataTransformation, "normalizedata")

    def test_registration(self) -> None:
        """Tests transformations registration."""
        registration_test(NormalizeDataTransformation, "normalizedata")
