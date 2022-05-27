"""Tests for unary transformations."""
import copy
import logging
from typing import Optional, Type

from _pytest.logging import LogCaptureFixture
from marshmallow import ValidationError
import pytest

from bitfount.transformations.base_transformation import (
    MultiColumnOutputTransformation,
    Transformation,
)
from bitfount.transformations.unary_operations import (
    InclusionTransformation,
    OneHotEncodingTransformation,
    StringUnaryOperation,
)
from tests.bitfount.transformations.transformation_test_helpers import (
    gen_name_fails,
    gen_name_test,
    registration_test,
)
from tests.utils.helper import unit_test


def gen_name_test_unary(cls: Type[Transformation], registry_name: str) -> None:
    """Tests name generation for unary transformations.

    Tests that a unary transformation class is created with the correctly generated
    random name.
    """
    gen_name_test(cls, registry_name, arg="hello")


@unit_test
class TestStringUnaryOperation:
    """Tests for StringUnaryOperation abstract transformation."""

    def test__gen_name_fails(self) -> None:
        """Tests that name generation fails."""
        gen_name_fails(StringUnaryOperation)

    def test_schema_loads(self) -> None:
        """Test schema load works correctly."""
        s = StringUnaryOperation.schema()
        t = s.loads(
            """
            name: test
            output: True
            arg: hello
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.arg == "hello"

    def test_schema_load_fails_arg_nonstring(self) -> None:
        """Tests schema load fails if arg isn't a string."""
        s = StringUnaryOperation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                arg: 1
                """
            )

    def test_schema_load_fails_missing_arg(self) -> None:
        """Tests schema load fails if arg missing."""
        s = StringUnaryOperation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                """
            )


@unit_test
class TestOneHotEncodingTransformation:
    """Tests for the OneHotEncodingTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        # Test that name gen not attempted if no name and no reference provided.
        with pytest.raises(
            ValueError, match="No name provided and no reference found in arg."
        ):
            gen_name_test(
                OneHotEncodingTransformation,
                "onehotencode",
                arg="hello",
                raw_values=["blah"],
            )

        # Test that name gen attempted if reference provided.
        t = OneHotEncodingTransformation(arg="c:hello", raw_values=["blah"])
        assert t.name == "onehotencode_FAKE_HEX"

    def test_registration(self) -> None:
        """Tests transformation registration."""
        registration_test(OneHotEncodingTransformation, "onehotencode")

    def test_is_multi_column_output(self) -> None:
        """Tests one-hot encoding correctly marked as multi-column output."""
        assert issubclass(OneHotEncodingTransformation, MultiColumnOutputTransformation)
        assert isinstance(
            OneHotEncodingTransformation(
                name="ohe_test", arg="test", raw_values=["blah"]
            ),
            MultiColumnOutputTransformation,
        )

    def test_init(self) -> None:
        """Tests that OHE is correctly initialized with various arg-types."""
        t_name: Optional[str]

        # With name
        t_name = "ohe_test"
        t_arg = "random_name"
        # With list `raw_values`
        ohe = OneHotEncodingTransformation(name=t_name, arg=t_arg, raw_values=[1, 2, 3])
        assert ohe.values == {i: f"{t_name}_{i}" for i in [1, 2, 3]}

        # With dict `raw_values`
        ohe = OneHotEncodingTransformation(
            name=t_name, arg=t_arg, raw_values={1: "hello", 2: "world"}
        )
        assert ohe.values == {
            k: f"{t_name}_{v}" for k, v in {1: "hello", 2: "world"}.items()
        }

        # With dict with Nones `raw_values`
        ohe = OneHotEncodingTransformation(
            name=t_name, arg=t_arg, raw_values={1: "hello", 2: None}
        )
        assert ohe.values == {
            k: f"{t_name}_{v}" for k, v in {1: "hello", 2: "2"}.items()
        }

        # With ref arg
        t_name = None
        t_ref = "ref_test"
        t_arg = f"c:{t_ref}"
        # With list `raw_values`
        ohe = OneHotEncodingTransformation(name=t_name, arg=t_arg, raw_values=[1, 2, 3])
        assert ohe.values == {i: f"{t_ref}_{i}" for i in [1, 2, 3]}

        # With dict `raw_values`
        ohe = OneHotEncodingTransformation(
            name=t_name, arg=t_arg, raw_values={1: "hello", 2: "world"}
        )
        assert ohe.values == {
            k: f"{t_ref}_{v}" for k, v in {1: "hello", 2: "world"}.items()
        }

        # With dict with Nones `raw_values`
        ohe = OneHotEncodingTransformation(
            name=t_name, arg=t_arg, raw_values={1: "hello", 2: None}
        )
        assert ohe.values == {
            k: f"{t_ref}_{v}" for k, v in {1: "hello", 2: "2"}.items()
        }

    def test_init_fails_duplicate_values(self) -> None:
        """Tests that initialization fails if duplicate values are provided."""
        # Test list `raw_values`
        with pytest.raises(
            ValueError, match="If `raw_values` is a list, elements must be unique."
        ):
            OneHotEncodingTransformation(
                name="ohe_test", arg="_unused", raw_values=[1, 1]
            )

        # Test dict `raw_values`
        with pytest.raises(ValueError, match="Column names generated must be unique:"):
            OneHotEncodingTransformation(
                name="ohe_test", arg="_unused", raw_values={1: "hello", 2: "hello"}
            )

        # Test dict with None `raw_values`
        with pytest.raises(ValueError, match="Column names generated must be unique:"):
            OneHotEncodingTransformation(
                name="ohe_test", arg="_unused", raw_values={1: "hello", "hello": None}
            )

    def test_init_fails_if_unknown_col_clash(self) -> None:
        """Tests that initialization fails if col clashes with unknown col."""
        # Test list `raw_values`
        with pytest.raises(
            ValueError,
            match="At least one column name clashes with the unknown value column",
        ):
            OneHotEncodingTransformation(
                name="ohe_test", arg="_unused", raw_values=["UNKNOWN"]
            )

        # Test dict `raw_values`
        with pytest.raises(
            ValueError,
            match="At least one column name clashes with the unknown value column",
        ):
            OneHotEncodingTransformation(
                name="ohe_test", arg="_unused", raw_values={1: "UNKNOWN"}
            )

        # Test dict with None `raw_values`
        with pytest.raises(
            ValueError,
            match="At least one column name clashes with the unknown value column",
        ):
            OneHotEncodingTransformation(
                name="ohe_test", arg="_unused", raw_values={"UNKNOWN": None}
            )

    def test_init_fails_if_no_name_and_non_ref_arg(self) -> None:
        """Tests the init fails if no name and non-reference arg."""
        with pytest.raises(
            ValueError, match="No name provided and no reference found in arg."
        ):
            OneHotEncodingTransformation(arg="not_a_ref", raw_values=["blah"])

    def test_init_fails_if_no_raw_values(self) -> None:
        """Tests the init fails if no raw_values are provided."""
        # Test with list raw_values
        with pytest.raises(
            ValueError, match="At least one value must be provided to one-hot encode."
        ):
            OneHotEncodingTransformation(name="name", arg="arg", raw_values=[])

        # Test with dict raw_values
        with pytest.raises(
            ValueError, match="At least one value must be provided to one-hot encode."
        ):
            OneHotEncodingTransformation(name="name", arg="arg", raw_values={})

    def test_columns_with_name_provided(self) -> None:
        """Tests the columns property when name provided."""
        t_name = "ohe_test"

        # Test when `raw_values` is a list
        ohe = OneHotEncodingTransformation(name=t_name, arg="", raw_values=[1, 2, 3])
        assert ohe.columns == [f"{t_name}_{i}" for i in [1, 2, 3]] + [
            f"{t_name}_UNKNOWN"
        ]

        # Test when `raw_values` is a dict
        ohe = OneHotEncodingTransformation(
            name=t_name, arg="", raw_values={1: "hello", 2: "world"}
        )
        assert ohe.columns == [f"{t_name}_{i}" for i in ["hello", "world"]] + [
            f"{t_name}_UNKNOWN"
        ]

        # Test when `raw_values` is a dict with Nones
        ohe = OneHotEncodingTransformation(
            name=t_name, arg="", raw_values={1: "hello", 2: None}
        )
        assert ohe.columns == [f"{t_name}_{i}" for i in ["hello", 2]] + [
            f"{t_name}_UNKNOWN"
        ]

    def test_columns_with_name_not_provided_but_arg_ref(self, fake_uuid: None) -> None:
        """Tests the columns property when no name provided but arg is a reference."""
        ref = "test"
        arg_ref = f"c:{ref}"

        # Test when `raw_values` is a list
        ohe = OneHotEncodingTransformation(arg=arg_ref, raw_values=[1, 2, 3])
        assert ohe.columns == [f"{ref}_{i}" for i in [1, 2, 3]] + [f"{ref}_UNKNOWN"]

        # Test when `raw_values` is a dict
        ohe = OneHotEncodingTransformation(
            arg=arg_ref, raw_values={1: "hello", 2: "world"}
        )
        assert ohe.columns == [f"{ref}_{i}" for i in ["hello", "world"]] + [
            f"{ref}_UNKNOWN"
        ]

        # Test when `raw_values` is a dict with Nones
        ohe = OneHotEncodingTransformation(
            arg=arg_ref, raw_values={1: "hello", 2: None}
        )
        assert ohe.columns == [f"{ref}_{i}" for i in ["hello", 2]] + [f"{ref}_UNKNOWN"]

    def test_prefix(self) -> None:
        """Tests prefix property."""
        # If name provided
        ohe = OneHotEncodingTransformation(
            name="ohe_test", arg="", raw_values=["_value"]
        )
        assert ohe.prefix == "ohe_test"

        # If no name but ref arg was provided
        ohe = OneHotEncodingTransformation(arg="c:test", raw_values=["_value"])
        assert ohe.prefix == "test"

        # If no name or ref arg was provided
        with pytest.raises(
            ValueError, match="No name provided and no reference found in arg."
        ):
            OneHotEncodingTransformation(arg="not_a_ref", raw_values=["_value"])

    def test_unknown_col(self) -> None:
        """Tests unknown_col property."""
        ohe = OneHotEncodingTransformation(
            name="ohe_test", arg="", raw_values=["_value"]
        )
        assert ohe.unknown_col == f"{ohe.prefix}_UNKNOWN"

    def test_unknown_col_custom_suffix(self) -> None:
        """Tests unknown_col property with custom suffix."""
        ohe = OneHotEncodingTransformation(
            name="ohe_test", arg="", raw_values=["_value"], unknown_suffix="CUSTOM"
        )
        assert ohe.unknown_col == f"{ohe.prefix}_CUSTOM"

    def test_trying_to_init_values_twice(self, caplog: LogCaptureFixture) -> None:
        """Tests that values cannot be set twice."""
        ohe = OneHotEncodingTransformation(
            name="ohe_test", arg="_unused", raw_values=[1, 2, 3]
        )
        orig_values = copy.deepcopy(ohe.values)

        # Try to init again
        with caplog.at_level(logging.WARNING):
            ohe._produce_full_col_map()

        log_record = caplog.records[0]
        assert log_record.levelname == "WARNING"
        assert (
            log_record.message
            == "_produce_full_col_map should not be called more than once"
        )
        assert orig_values == ohe.values

    # The tests below this point are all related to the schema validation. It
    # duplicates many of the tests in the transformation hierarchy but is needed
    # here because OneHotEncodingTransformation has a custom schema.
    def test_schema_loads_list_values(self) -> None:
        """Test schema load works correctly with list values."""
        s = OneHotEncodingTransformation.schema()
        t = s.loads(
            """
            name: test
            output: True
            arg: hello
            values: [ 1, 2, 3 ]
            unknown_suffix: UNKNOWN_TEST
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.arg == "hello"
        assert t.values == {i: f"test_{i}" for i in [1, 2, 3]}
        assert t.unknown_suffix == "UNKNOWN_TEST"

    def test_schema_loads_dict_values(self) -> None:
        """Test schema load works correctly with dict values."""
        s = OneHotEncodingTransformation.schema()
        t = s.loads(
            """
            name: test
            output: True
            arg: hello
            values: { 1: "hello", 2: "world" }
            unknown_suffix: UNKNOWN_TEST
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.arg == "hello"
        assert t.values == {k: f"test_{v}" for k, v in {1: "hello", 2: "world"}.items()}
        assert t.unknown_suffix == "UNKNOWN_TEST"

    def test_schema_loads_dict_null_values(self) -> None:
        """Test schema load works correctly with null dict values."""
        s = OneHotEncodingTransformation.schema()
        t = s.loads(
            """
            name: test
            output: True
            arg: hello
            values:
              1: hello
              2:
            unknown_suffix: UNKNOWN_TEST
            """
        )
        assert t.name == "test"
        assert t.output is True
        assert t.arg == "hello"
        assert t.values == {k: f"test_{v}" for k, v in {1: "hello", 2: "2"}.items()}
        assert t.unknown_suffix == "UNKNOWN_TEST"

    def test_schema_load_succeeds_without_name(self, fake_uuid: None) -> None:
        """Tests schema loads successfully without name field."""
        s = OneHotEncodingTransformation.schema()
        t = s.loads(
            """
            output: True
            arg: c:hello
            values: [ 1, 2, 3 ]
            """
        )
        assert t.name == "onehotencode_FAKE_HEX"
        assert t.output is True

    def test_schema_load_fails_with_wrong_type_name(self) -> None:
        """Tests schema load fails if non-str name field."""
        s = OneHotEncodingTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: 2
                arg: hello
                values: [ 1, 2, 3 ]
                """
            )

    def test_schema_load_succeeds_without_output(self) -> None:
        """Tests schema loads successfully without output field."""
        s = OneHotEncodingTransformation.schema()
        t = s.loads(
            """
            name: test
            arg: hello
            values: [ 1, 2, 3 ]
            """
        )
        assert t.name == "test"
        assert t.output is False

    def test_schema_load_fails_with_wrong_type_output(self) -> None:
        """Tests schema load fails if non-bool output field."""
        s = OneHotEncodingTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: hello
                arg: hello
                values: [ 1, 2, 3 ]
                """
            )

    def test_schema_load_fails_missing_arg(self) -> None:
        """Tests schema load fails if arg missing."""
        s = OneHotEncodingTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                values: [ 1, 2, 3 ]
                """
            )

    def test_schema_load_fails_arg_nonstring(self) -> None:
        """Tests schema load fails if arg isn't a string."""
        s = OneHotEncodingTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                arg: 1
                values: [ 1, 2, 3 ]
                """
            )

    def test_schema_load_fails_missing_values(self) -> None:
        """Tests schema load fails if values is missing."""
        s = OneHotEncodingTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                arg: hello
                """
            )

    def test_schema_load_fails_values_wrong_type(self) -> None:
        """Tests schema load fails if values is an incompatible type."""
        s = OneHotEncodingTransformation.schema()

        # Values is non-list, non-dict
        with pytest.raises(ValidationError):
            s.loads(
                """
                arg: hello
                values: 1
                """
            )

        # Values is dict but with non-str values
        with pytest.raises(ValidationError):
            s.loads(
                """
                arg: hello
                values: { 1: 1 }
                """
            )

        # Values is null
        with pytest.raises(ValidationError):
            s.loads(
                """
                arg: hello
                values: null
                """
            )

    def test_schema_load_succeeds_without_unknown_suffix(self) -> None:
        """Tests schema loads successfully without unknown_suffix field."""
        s = OneHotEncodingTransformation.schema()
        t = s.loads(
            """
            name: test
            arg: hello
            values: [ 1, 2, 3 ]
            """
        )
        assert t.unknown_suffix == "UNKNOWN"

    def test_schema_load_fails_unknown_suffix_non_string(self) -> None:
        """Tests schema load fails if unknown_suffix isn't a string."""
        s = OneHotEncodingTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                arg: hello
                values: [ 1, 2, 3 ]
                unknown_suffix: false
                """
            )


@unit_test
class TestInclusionTransformation:
    """Tests for the InclusionTransformation class."""

    def test__gen_name(self, fake_uuid: None) -> None:
        """Tests transformation name generation."""
        gen_name_test(InclusionTransformation, "in", arg="hello", in_str="hell")

    def test_registration(self) -> None:
        """Tests transformation registration."""
        registration_test(InclusionTransformation, "in")

    def test_schema_load_fails_arg2_nonstring(self) -> None:
        """Tests schema load fails if arg2 is not a string."""
        s = InclusionTransformation.schema()
        with pytest.raises(ValidationError):
            s.loads(
                """
                name: test
                output: True
                arg1: hello
                arg2: 2
                """
            )
