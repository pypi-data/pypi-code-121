"""Tests for binary transformations."""
from typing import Type

from marshmallow import ValidationError
import pytest

from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.binary_operations import (
    AdditionTransformation,
    BinaryOperation,
    ComparisonTransformation,
    DivisionTransformation,
    MultiplicationTransformation,
    NumericBinaryOperation,
    SubtractionTransformation,
)
from tests.bitfount.transformations.transformation_test_helpers import (
    gen_name_fails,
    gen_name_test,
    registration_test,
)
from tests.utils.helper import unit_test


@unit_test
class TestBinaryOperation:
    """Tests for the BinaryOperation abstract transformation."""

    def test__gen_name_fails(self) -> None:
        """Tests that name generation fails."""
        gen_name_fails(BinaryOperation)


@unit_test
class TestNumericBinaryOperation:
    """Tests for the NumericBinaryOperation abstract transformation."""

    def test__gen_name_fails(self) -> None:
        """Tests that name generation fails."""
        gen_name_fails(NumericBinaryOperation)

    def test_schema_loads(self) -> None:
        """Tests schema loads correctly."""
        s = NumericBinaryOperation.schema()
        t = s.loads(
            """
            name: test
            output: True
            arg1: hello
            arg2: world
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.arg1 == "hello"
        assert t.arg2 == "world"

    def test_schema_loads_arg2_numeric(self) -> None:
        """Tests schema loads if arg2 is a number."""
        s = NumericBinaryOperation.schema()
        t = s.loads(
            """
            name: test
            output: True
            arg1: hello
            arg2: 2
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.arg1 == "hello"
        assert t.arg2 == 2.0

    def test_schema_load_fails_arg1_nonstring(self) -> None:
        """Tests schema load fails if arg1 isn't a string."""
        s = NumericBinaryOperation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                arg1: 1
                arg2: world
                """
            )

    def test_schema_load_fails_arg2_wrong_type(self) -> None:
        """Tests schema load fails if arg2 isn't a float or str."""
        s = NumericBinaryOperation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                arg1: hello
                arg2: []
                """
            )

    def test_schema_load_fails_missing_arg1(self) -> None:
        """Tests schema load fails if missing arg1."""
        s = NumericBinaryOperation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                arg2: world
                """
            )

    def test_schema_load_fails_missing_arg2(self) -> None:
        """Tests schema load fails if missing arg2."""
        s = NumericBinaryOperation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                arg1: hello
                """
            )


def gen_name_test_binary(cls: Type[Transformation], registry_name: str) -> None:
    """Tests name generation for binary transformations.

    Test that a binary transformation class is created with the correctly generated
    random name.
    """
    gen_name_test(cls, registry_name, arg1="hello", arg2="world")


@unit_test
class TestAdditionTransformation:
    """Tests for the AdditionTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_binary(AdditionTransformation, "add")

    def test_registration(self) -> None:
        """Tests transformation registration."""
        registration_test(AdditionTransformation, "add")


@unit_test
class TestSubtractionTransformation:
    """Tests for the SubtractionTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_binary(SubtractionTransformation, "subtract")

    def test_registration(self) -> None:
        """Tests transformation registration."""
        registration_test(SubtractionTransformation, "subtract")


@unit_test
class TestMultiplicationTransformation:
    """Tests for the MultiplicationTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_binary(MultiplicationTransformation, "multiply")

    def test_registration(self) -> None:
        """Tests transformations registration."""
        registration_test(MultiplicationTransformation, "multiply")


@unit_test
class TestDivisionTransformation:
    """Tests for the DivisionTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_binary(DivisionTransformation, "divide")

    def test_registration(self) -> None:
        """Tests transformation registration."""
        registration_test(DivisionTransformation, "divide")


@unit_test
class TestComparisonTransformation:
    """Tests for the ComparisonTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test_binary(ComparisonTransformation, "compare")

    def test_registration(self) -> None:
        """Tests transformation registration."""
        registration_test(ComparisonTransformation, "compare")
