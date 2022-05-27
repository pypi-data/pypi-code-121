"""Tests for the transformation parsing."""
from pathlib import Path
from typing import Dict, Tuple

import pytest
from pytest import fixture
import yaml

from bitfount.data.types import DataSplit
from bitfount.transformations.batch_operations import ImageTransformation
from bitfount.transformations.binary_operations import (
    AdditionTransformation,
    DivisionTransformation,
)
from bitfount.transformations.exceptions import TransformationParsingError
from bitfount.transformations.parser import TransformationsParser
from bitfount.transformations.unary_operations import (
    InclusionTransformation,
    OneHotEncodingTransformation,
)
from tests.utils.helper import unit_test

test_yaml = """
Transformations:
- Add:
    name: col_1_and_2_sum
    output: false
    arg1: col:col_1
    arg2: c:col_2
- Divide:
    name: normalised_result
    output: true
    arg1: tran:col_1_and_2_sum
    arg2: 100
- In:
    in_str: "DAILY"
    arg: column:frequency
    output: true
"""

out_col_refs = {"col_1", "col_2", "frequency"}


@fixture
def test_transformations(
    fake_uuid: None,
) -> Tuple[AdditionTransformation, DivisionTransformation, InclusionTransformation]:
    """Transformations for tests."""
    return (
        AdditionTransformation(
            name="col_1_and_2_sum", output=False, arg1="col:col_1", arg2="c:col_2"
        ),
        DivisionTransformation(
            name="normalised_result", output=True, arg1="tran:col_1_and_2_sum", arg2=100
        ),
        InclusionTransformation(output=True, in_str="DAILY", arg="column:frequency"),
    )


@fixture
def test_transformations_results(
    test_transformations: Tuple[
        AdditionTransformation, DivisionTransformation, InclusionTransformation
    ]
) -> Tuple[AdditionTransformation, DivisionTransformation, InclusionTransformation]:
    """Generate transformations where transformations are hooked together."""
    test_transformations[1].arg1 = test_transformations[0]  # type: ignore[assignment] # Reason: replacing str with Transformation is expected # noqa: B950
    return test_transformations


@fixture
def transformation_parser() -> TransformationsParser:
    """A TransformationsParser instance for tests."""
    return TransformationsParser()


@unit_test
class TestTransformationsParser:
    """Tests for the TransformationsParser class."""

    def test_parse(
        self,
        fake_uuid: None,
        test_transformations_results: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests parsing of transformations string works correctly."""
        transformations, col_refs = transformation_parser.parse(test_yaml)
        assert transformations == list(test_transformations_results)
        assert col_refs == out_col_refs

    def test_parse_file(
        self,
        fake_uuid: None,
        test_transformations_results: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        tmp_path: Path,
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests parse file works correctly."""
        test_file = tmp_path / "test.yml"
        with open(test_file, "w") as f:
            f.write(test_yaml)
        transformations, col_refs = transformation_parser.parse_file(test_file)
        assert transformations == list(test_transformations_results)
        assert col_refs == out_col_refs

    def test_deserialize_transformations(
        self,
        test_transformations_results: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests deserialize_transformations works correctly."""
        data = yaml.safe_load(test_yaml)["Transformations"]
        transformations, col_refs = transformation_parser.deserialize_transformations(
            data
        )
        assert transformations == list(test_transformations_results)
        assert col_refs == out_col_refs

    def test_deserialize_transformations_captures_errors(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests that all errors are captured and output at once."""
        bad_yaml = """
        Transformations:
        - UnknownTransform:
            name: unknown_1
        - Add:
            name: multi_transform_1
            arg1: test
            arg2: 100
          Divide:
            name: multi_transform_2
            arg1: test
            arg2: 100
        - Add:
            name: normalised_result
            arg1: test
            arg2: 100
        - Divide:
            name: normalised_result
            output: true
            arg1: tran:col_1_and_2_sum
            arg2: 100
        - In:
            in_str: "DAILY"
            arg: column:frequency
            output: true
        - OneHotEncode:
            name: normalised
            arg: column:is_normalised
            values: [result]
        """
        data = yaml.safe_load(bad_yaml)["Transformations"]
        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser.deserialize_transformations(data)
        assert tpe.value.errors == [
            f'No transformation registered with name {"UnknownTransform".lower()}.',
            "Each transformation mapping must contain exactly one transformation; "
            "mapping 1 contains 2.",
            "Duplicate transformation name: normalised_result.",
            "Multi-column output clash: normalised_result "
            "(from output column of normalised).",
            "Transformation, normalised_result, attempted to use transformation "
            '"col_1_and_2_sum" before it was defined.',
        ]

    def test__deserialize_transformation(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests _deserialize_transformation works correctly."""
        t_spec = {"Add": {"name": "add_test", "arg1": "arg1_test", "arg2": "arg2_test"}}
        t = transformation_parser._deserialize_transformation(0, t_spec)
        assert t == AdditionTransformation(
            name="add_test", arg1="arg1_test", arg2="arg2_test"
        )

    def test__deserialize_transformation_fails_on_multi_spec(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests deserialization fails if multiple specs in one transformation."""
        t_spec: Dict[str, dict] = {"Add": {}, "Divide": {}}
        with pytest.raises(TransformationParsingError):
            transformation_parser._deserialize_transformation(0, t_spec)

    def test__deserialize_transformation_fails_on_empty_spec(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests deserialization fails if a transformation spec is empty."""
        t_spec: Dict[str, dict] = {}
        with pytest.raises(TransformationParsingError):
            transformation_parser._deserialize_transformation(0, t_spec)

    def test__deserialize_transformation_fails_on_non_registered_transform(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests deserialization raises exception on unknown transformation."""
        t_spec: Dict[str, dict] = {"NotARealTransform": {}}
        with pytest.raises(TransformationParsingError):
            transformation_parser._deserialize_transformation(0, t_spec)

    def test__check_names_unique(
        self,
        test_transformations: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests _check_names_unique works correctly."""
        transformation_parser._check_names_unique(test_transformations)

    def test__check_names_unique_w_multi_column(
        self,
        test_transformations: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests _check_names_unique works correctly with multi-output columns."""
        aux_test_transformations = test_transformations + (
            OneHotEncodingTransformation(
                name="one_hot", arg="c:categorical", raw_values=["CAT_1", "CAT_2"]
            ),
        )
        transformation_parser._check_names_unique(aux_test_transformations)

    def test__check_names_unique_fails(
        self,
        test_transformations: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests _check_names_unique fails on duplicate names."""
        test_transformations[2].name = test_transformations[0].name
        test_transformations[1].name = test_transformations[0].name

        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser._check_names_unique(test_transformations)

        assert tpe.value.errors == [
            f"Duplicate transformation name: {test_transformations[0].name}."
        ]

    def test__check_names_unique_fails_w_multi_column_same_name(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests _check_names_unique fails on duplicate name in MCO."""
        test_transformations = [
            AdditionTransformation(
                name="col_1_and_2_sum", output=False, arg1="col:col_1", arg2="c:col_2"
            ),
            OneHotEncodingTransformation(
                name="col_1_and_2_sum", arg="c:categorical", raw_values=["_unused"]
            ),
        ]

        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser._check_names_unique(test_transformations)

        assert tpe.value.errors == ["Duplicate transformation name: col_1_and_2_sum."]

    def test__check_names_unique_fails_w_multi_column_clash(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests _check_names_unique fails in multi-column scenario.

        Fails if the output columns of a multi-column transformation output would
        clash with another column name.
        """
        test_transformations = [
            AdditionTransformation(
                name="col_1_and_2_sum", output=False, arg1="col:col_1", arg2="c:col_2"
            ),
            OneHotEncodingTransformation(
                name="col_1", arg="c:categorical", raw_values=["and_2_sum"]
            ),
        ]

        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser._check_names_unique(test_transformations)

        assert tpe.value.errors == [
            "Multi-column output clash: col_1_and_2_sum (from output column of col_1)."
        ]

    def test__check_names_unique_fails_w_multiple_multi_column_clash(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests _check_names_unique fails in multiple multi-column scenario.

        Fails if the output columns of a multi-column transformation output would
        clash with the output column(s) of another multi-column transformation.
        """
        # Test correctly fails if the second MCO clashes with the first,
        # but the first doesn't clash with a base.
        test_transformations = [
            AdditionTransformation(
                name="col_1_and_2_sum", output=False, arg1="col:col_1", arg2="c:col_2"
            ),
            OneHotEncodingTransformation(
                name="col_1", arg="c:categorical", raw_values=["not_a_clash"]
            ),
            OneHotEncodingTransformation(
                name="col_1_not_a", arg="c:categorical", raw_values=["clash"]
            ),
        ]

        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser._check_names_unique(test_transformations)

        assert tpe.value.errors == [
            "Multi-column output clash: col_1_not_a_clash "
            "(from output column of col_1_not_a)."
        ]

        # Test correctly fails if the second MCO clashes with the first,
        # and the first also clashes with a base.
        test_transformations = [
            AdditionTransformation(
                name="col_1_and_2_sum", output=False, arg1="col:col_1", arg2="c:col_2"
            ),
            OneHotEncodingTransformation(
                name="col_1", arg="c:categorical", raw_values=["and_2_sum"]
            ),
            OneHotEncodingTransformation(
                name="col_1_and", arg="c:categorical", raw_values=["2_sum"]
            ),
        ]

        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser._check_names_unique(test_transformations)

        assert tpe.value.errors == [
            "Multi-column output clash: col_1_and_2_sum "
            "(from output column of col_1).",
            "Multi-column output clash: col_1_and_2_sum "
            "(from output column of col_1_and).",
        ]

    def test__hook_transformations_together(
        self,
        fake_uuid: None,
        test_transformations: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests _hook_transformations_together works correctly."""
        transformation_parser._hook_transformations_together(test_transformations)

        # First and last transformations unchanged
        assert test_transformations[0] == AdditionTransformation(
            name="col_1_and_2_sum", output=False, arg1="col:col_1", arg2="c:col_2"
        )
        assert test_transformations[2] == InclusionTransformation(
            output=True, in_str="DAILY", arg="column:frequency"
        )

        # Second transformation now references first, otherwise same
        orig_second = DivisionTransformation(
            name="normalised_result", output=True, arg1="tran:col_1_and_2_sum", arg2=100
        )
        assert test_transformations[1].name == orig_second.name
        assert test_transformations[1].output == orig_second.output
        assert test_transformations[1].arg2 == orig_second.arg2
        assert test_transformations[1].arg1 == test_transformations[0]

    def test__hook_transformations_together_fails_forward_ref(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests that parsing fails with exception if cols are forward referenced."""
        transformations = [
            AdditionTransformation(name="add", arg1="t:test", arg2=""),
            DivisionTransformation(name="div", arg1="tran:test", arg2=""),
            InclusionTransformation(name="test", in_str="", arg=""),
        ]

        with pytest.raises(TransformationParsingError) as tpe:
            transformation_parser._hook_transformations_together(transformations)

        assert tpe.value.errors == [
            f'Transformation, {name}, attempted to use transformation "{ref}" '
            f"before it was defined."
            for name, ref in [("add", "test"), ("div", "test")]
        ]

    def test__extract_column_refs(
        self,
        test_transformations: Tuple[
            AdditionTransformation, DivisionTransformation, InclusionTransformation
        ],
        transformation_parser: TransformationsParser,
    ) -> None:
        """Tests that _extract_column_refs() works correctly."""
        col_refs = transformation_parser._extract_column_refs(test_transformations)
        assert col_refs == out_col_refs


@unit_test
class TestTransformationParsingError:
    """Tests for the TransformationParsingError exception."""

    def test_single_error_arg(self) -> None:
        """Tests creation of TransformationParsingError with a single error."""
        with pytest.raises(TransformationParsingError) as tpe:
            raise TransformationParsingError("test")
        assert tpe.value.errors == ["test"]

    def test_multiple_error_arg(self) -> None:
        """Tests creation of TransformationParsingError with multiple errors."""
        with pytest.raises(TransformationParsingError) as tpe:
            raise TransformationParsingError(["test", "test2"])
        assert tpe.value.errors == ["test", "test2"]

    def test_str(self) -> None:
        """Tests string representation of TransformationParsingError."""
        with pytest.raises(TransformationParsingError) as tpe:
            raise TransformationParsingError(["test", "test2"])
        assert str(tpe.value) == "Errors: \ntest\ntest2"


@unit_test
class TestParsingBatchTransformations:
    """Tests parsing of batch transformations."""

    def test_parsing_image_transformation_successfully(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests parsing of image transformation succesfully."""
        transformations_yaml = """
        Transformations:
            - Image:
                arg: col:col_1
                name: test_col
                step: train
                output: True
                transformations:
                    - ResizeTransformation:
                        arg1: 1
                        arg2: 2
                    - NormalizeTransformation
        """
        tfms, _ = transformation_parser.parse(transformations_yaml)
        assert tfms[0] == ImageTransformation(
            name="test_col",
            output=True,
            arg="col:col_1",
            step=DataSplit.TRAIN,
            transformations=[
                {"ResizeTransformation": {"arg1": 1, "arg2": 2}},
                "NormalizeTransformation",
            ],
        )

    def test_image_transformation_output_must_be_true(
        self, transformation_parser: TransformationsParser
    ) -> None:
        """Tests that output must be True for Image Transformation."""
        transformations_yaml = """
        Transformations:
            - Image:
                arg: col:col_1
                name: test_col
                step: train
                output: False
                transformations:
                    - ResizeTransformation:
                        arg1: 1
                        arg2: 2
                    - NormalizeTransformation
        """
        with pytest.raises(
            ValueError, match="`output` cannot be False for a BatchTimeOperation"
        ):
            transformation_parser.parse(transformations_yaml)
