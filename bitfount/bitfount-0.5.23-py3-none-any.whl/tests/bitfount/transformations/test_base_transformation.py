"""Tests for the base transformation classes."""
from marshmallow import Schema as MarshmallowSchema
from marshmallow import ValidationError
import pytest

from bitfount.transformations.base_transformation import (
    Transformation,
    _TransformationSchema,
)
from bitfount.transformations.exceptions import TransformationRegistryError
from tests.bitfount.transformations.transformation_test_helpers import gen_name_fails
from tests.utils.helper import unit_test


@unit_test
class TestTransformationRegistry:
    """Tests for the functionality of the transformation registry."""

    def test_transformations_are_registered(self, empty_registry: None) -> None:
        """Tests that concrete transformation classes are correctly registered."""
        from bitfount.transformations.base_transformation import (
            TRANSFORMATION_REGISTRY,
            Transformation,
        )

        class Test(Transformation):
            _registry_name = "test"

        class Test_2(Transformation):
            _registry_name = "test_2"

        assert TRANSFORMATION_REGISTRY == {"test": Test, "test_2": Test_2}

    def test_transformation_registry_names_unique(self, empty_registry: None) -> None:
        """Tests that transformation registry names are unique.

        Tests exception is raised if multiple concrete transformations attempt to
        register with same name.
        """
        from bitfount.transformations.base_transformation import Transformation

        class _Test(Transformation):
            _registry_name = "test"

        with pytest.raises(
            TransformationRegistryError,
            match='A transformation is already registered with name "test"',
        ):

            class _Test_2(Transformation):
                _registry_name = "test"

    def test_non_concrete_transformations_not_registered(
        self, empty_registry: None
    ) -> None:
        """Tests non-concrete classes aren't registered."""
        from bitfount.transformations.base_transformation import (
            TRANSFORMATION_REGISTRY,
            Transformation,
        )

        class _AbstractTest(Transformation):
            pass

        assert TRANSFORMATION_REGISTRY == {}


@unit_test
class TestTransformation:
    """Tests the base transformation class."""

    def test_schema_loads(self) -> None:
        """Tests schema load works correctly."""
        s = Transformation.schema()
        t = s.loads(
            """
            name: test
            output: True
            """
        )
        assert t.name == "test"
        assert t.output is True

    def test_schema_load_fails_without_name(self) -> None:
        """Tests schema loading fails without name field."""
        s = Transformation.schema()
        with pytest.raises(
            TransformationRegistryError,
            match="Transformation .* isn't registered; can't generate name",
        ):
            s.loads(
                """
                output: True
                """
            )

    def test_schema_load_succeeds_without_output(self) -> None:
        """Tests schema loads successfully without output field."""
        s = Transformation.schema()
        t = s.loads(
            """
            name: test
            """
        )
        assert t.name == "test"
        assert t.output is False

    def test_schema_load_fails_with_wrong_type_name(self) -> None:
        """Tests schema load fails if non-str name field."""
        s = Transformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: 2
                output: True
                """
            )

    def test_schema_load_fails_with_wrong_type_output(self) -> None:
        """Tests schema load fails if non-bool output field."""
        s = Transformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: hello
                """
            )

    def test__gen_name_fails(self) -> None:
        """Tests that name generation fails."""
        gen_name_fails(Transformation)

    def test_custom_schema_loads(self) -> None:
        """Tests that if a custom schema is defined, it is the one loaded."""

        class CustomTransformation(Transformation):
            class _Schema(_TransformationSchema):
                pass

        s = CustomTransformation.schema()
        assert isinstance(s, CustomTransformation._Schema)

    def test_custom_schema_must_subclass_transformation_schema(self) -> None:
        """Tests that error raised if custom schema isn't a TransformationSchema."""

        class CustomTransformation(Transformation):
            class _Schema(MarshmallowSchema):
                pass

        with pytest.raises(TypeError, match="must be a TransformationSchema instance."):
            CustomTransformation.schema()
