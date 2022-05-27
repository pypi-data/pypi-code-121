"""Tests for transformation processing."""
from typing import Mapping, Tuple, Type, Union, cast

from PIL import Image
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal
import pytest
from pytest import fixture

from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.schema import BitfountSchema, TableSchema
from bitfount.data.types import DataSplit
from bitfount.transformations.dataset_operations import (
    NormalizeDataTransformation,
    ScalarAdditionDataTransformation,
    ScalarMultiplicationDataTransformation,
)
from bitfount.transformations.exceptions import (
    InvalidBatchTransformationError,
    MissingColumnReferenceError,
    TransformationApplicationError,
    TransformationProcessorError,
)
from bitfount.transformations.parser import TransformationsParser
from bitfount.transformations.processor import TransformationProcessor
from bitfount.transformations.unary_operations import OneHotEncodingTransformation
from tests.utils import PytestRequest
from tests.utils.helper import create_dataset, integration_test, unit_test


def parse_and_process_data(
    data: pd.DataFrame, schema: TableSchema, transformations_yaml: str
) -> Tuple[pd.DataFrame, TableSchema]:
    """Parses transformations YAML and applies them to data."""
    parser = TransformationsParser()
    transformations, cols = parser.parse(transformations_yaml)
    processor = TransformationProcessor(transformations, schema, cols)
    data = processor.transform(data)
    return data, cast(TableSchema, processor.schema)


IntegerTypes = Tuple[
    Type[int], Type[np.int32], Type[np.int64], pd.Int32Dtype, pd.Int64Dtype
]


class TestTransformationProcessor:
    """Tests for TransformationProcessor class."""

    @fixture(scope="function")
    def data_and_schema(
        self, request: PytestRequest
    ) -> Tuple[pd.DataFrame, TableSchema]:
        """Dataset and schema to be used for tests."""
        data = create_dataset()
        datasource = DataFrameSource(data)
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name="test")
        datasource.load_data()
        return datasource.data, schema.tables[0]

    @fixture
    def integer_types(self) -> IntegerTypes:
        """Fixture determining what counts as an integer type."""
        return (int, np.int32, np.int64, pd.Int32Dtype(), pd.Int64Dtype())

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_addition_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests addition transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - Add:
            name: A_and_B_sum
            output: true
            arg1: col:A
            arg2: c:B
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "A_and_B_sum" in data.columns
        assert data["A_and_B_sum"].sum() == data.A.sum() + data.B.sum()

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_comparison_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests comparison transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - Compare:
            name: A_and_B_comp
            output: true
            arg1: col:A
            arg2: c:B
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "A_and_B_comp" in data.columns
        comp = sum((data.A > data.B).to_list()) - sum((data.B > data.A).to_list())
        assert data["A_and_B_comp"].sum() == comp

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_comparison_transformation_with_constant(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests comparison transformation works correctly with a constant."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - Compare:
            name: A_and_2_comp
            output: true
            arg1: col:A
            arg2: 2
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "A_and_2_comp" in data.columns
        comp = sum((data.A > 2).to_list()) - sum((data.A < 2).to_list())
        assert data["A_and_2_comp"].sum() == comp

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_division_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests division transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - Divide:
            name: A_and_B_div
            output: true
            arg1: col:A
            arg2: c:B
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "A_and_B_div" in data.columns
        assert int(data["A_and_B_div"].sum()) == int(
            np.sum((data.A / data.B).to_numpy())
        )

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_inclusion_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests inclusion transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - In:
            name: a_in_I
            output: true
            in_str: a
            arg: c:I
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "a_in_I" in data.columns
        assert sum(data["a_in_I"].to_list()) == sum((data.I == "a").to_list())

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_multiplication_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests multiplication transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - Multiply:
            name: A_and_B_prod
            output: true
            arg1: col:A
            arg2: c:B
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "A_and_B_prod" in data.columns
        assert data["A_and_B_prod"].sum() == data.A @ data.B

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_one_hot_encoding_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests one-hot encoding transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - OneHotEncode:
            name: ohe_I
            output: true
            arg: col:I
            values: [e,f,g]
        """
        original_data_len = len(data.index)
        data, _ = parse_and_process_data(data, schema, test_yaml)

        # Check all one hot columns are included
        one_hot_cols = [f"ohe_I_{letter}" for letter in [*"efg", "UNKNOWN"]]
        for col in one_hot_cols:
            assert col in data.columns

        # Check no others are
        for col in data.columns:
            if col.startswith("ohe"):
                assert col in one_hot_cols

        # Check additional columns have been correctly concatenated
        assert len(data.index) == original_data_len

    @fixture
    def ohe_mini_dataset_and_results(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Provides a small dataset, results and dataframe type for tests.

        Generates a (4,3) test dataframe for testing one-hot encoding and a
        corresponding results dataframe (4,7) which encodes values [1, 2] from
        "col1".

        Also returns the type of the dataframes.
        """
        data_in = {
            "col1": [1, 2, 3, None],
            "col2": [4, 5, 6, None],
            "col3": [7, 8, 9, None],
        }
        results = {
            "col1": [1, 2, 3, None],
            "col2": [4, 5, 6, None],
            "col3": [7, 8, 9, None],
            "col1_1": [1, 0, 0, 0],
            "col1_2": [0, 1, 0, 0],
            "col1_UNKNOWN": [0, 0, 1, 0],
        }

        return (
            pd.DataFrame(data=data_in),
            pd.DataFrame(data=results),
        )

    @unit_test
    def test__do_one_hot_encoding(
        self,
        ohe_mini_dataset_and_results: Tuple[pd.DataFrame, pd.DataFrame],
    ) -> None:
        """Tests the one hot encoding method directly.

        Checks that values are being encoded correctly.
        """
        data_in, expected_results = ohe_mini_dataset_and_results

        ohe_transform = OneHotEncodingTransformation(arg="c:col1", raw_values=[1, 2])
        results = TransformationProcessor._do_one_hot_encoding(data_in, ohe_transform)

        assert_frame_equal(results, expected_results, check_dtype=False)

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_subtraction_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests subtraction transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - Subtract:
            name: A_and_B_sub
            output: true
            arg1: col:A
            arg2: c:B
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "A_and_B_sub" in data.columns
        assert data["A_and_B_sub"].sum() == data.A.sum() - data.B.sum()

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_cleandata_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests clean data transformation works correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - CleanData:
            name: cleandata
            cols: col:Date
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "cleandata" not in data.columns
        assert data["Date"].isnull().sum() == 0

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_cleandata_transformation_no_args(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests clean data transformation with no arguments (i.e. all cols)."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - CleanData
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert data["Date"].isnull().sum() == 0

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_normalize_transformation(
        self,
        data_and_schema: Tuple[pd.DataFrame, TableSchema],
        integer_types: IntegerTypes,
    ) -> None:
        """Tests normalize transformation works."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - NormalizeData:
            name: blah
            cols:
                - col:A
                - col:B
        """
        # Assert columns
        for col in ["A", "B", "C", "D"]:
            assert schema.features["continuous"][col].dtype in integer_types
        data, schema = parse_and_process_data(data, schema, test_yaml)
        assert round(data.A.mean()) == 0
        assert round(data.A.std()) == 1
        assert round(data.B.mean()) == 0
        assert round(data.B.std()) == 1

        # Assert that only columns A and B have been normalized
        assert schema.features["continuous"]["A"].dtype == np.float64
        assert schema.features["continuous"]["B"].dtype == np.float64
        assert schema.features["continuous"]["C"].dtype in integer_types
        assert schema.features["continuous"]["D"].dtype in integer_types

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_normalize_transformation_on_categorical_column(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests exception raised if normalize called on categorical column."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - NormalizeData:
            name: blah
            cols:
                - col:I
        """
        with pytest.raises(TransformationApplicationError):
            parse_and_process_data(data, schema, test_yaml)

    @unit_test
    def test_normalize_transformation_with_list_of_cols(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests normalization works when instantiated with a list of columns."""
        data, schema = data_and_schema
        transform = NormalizeDataTransformation(cols=["A", "B"])
        processor = TransformationProcessor([transform], schema)
        data = processor.transform(data)
        assert round(data["A"].mean()) == 0
        assert round(data["A"].std()) == 1
        assert round(data["B"].mean()) == 0
        assert round(data["B"].std()) == 1

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_normalize_transformation_no_args(
        self,
        data_and_schema: Tuple[pd.DataFrame, TableSchema],
        integer_types: IntegerTypes,
    ) -> None:
        """Tests NormalizeData transformation when no args supplied (all cols)."""
        data, schema = data_and_schema
        data["E"] = 2 * data["E"]
        data["F"] = 5 * data["F"]
        data["G"] = 10 * data["G"]
        data["H"] = 3 * data["H"]
        # Check that the mean is no longer 0
        for feature in ["E", "F", "G", "H"]:
            assert round(data[feature].mean()) != 0
        test_yaml = """
        Transformations:
        - NormalizeData
        """
        data, schema = parse_and_process_data(data, schema, test_yaml)
        # Check that int columns remain unchanged
        for feature in ["A", "B", "C", "D"]:
            assert schema.features["continuous"][feature].dtype in integer_types
        # Check that the float columns have been normalized
        for feature in ["E", "F", "G", "H"]:
            assert round(data[feature].mean()) == 0
            assert round(data[feature].std()) == 1

    @unit_test
    def test_errors_if_transformation_same_name_as_col(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests an error is raised when a transformation name matches a column."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - add:
            name: A  # this matches a column name
            arg1: col:C
            arg2: col:D
        """
        with pytest.raises(TransformationApplicationError) as tpe:
            parse_and_process_data(data, schema, test_yaml)
        assert tpe.value.errors == [
            "Output column A, from transformation A, "
            "clashes with an existing data column name."
        ]

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_errors_if_multi_column_transformation_out_col_same_as_col(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests an error is raised when an MCO output column name matches a column."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - onehotencode:
            name: A  # this matches a column name, but doesn't matter
            arg: col:B
            values: {1: "C", 2: "D"}
        """
        # Rename data column to be problematic
        data = data.rename(columns={"C": "A_C", "D": "A_D"})

        with pytest.raises(TransformationApplicationError) as tpe:
            parse_and_process_data(data, schema, test_yaml)

        assert tpe.value.errors == [
            "Output column A_C, from transformation A, "
            "clashes with an existing data column name.",
            "Output column A_D, from transformation A, "
            "clashes with an existing data column name.",
        ]

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_multi_transformation(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the application of multiple transformations."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - divide:
            name: A_and_B_div
            output: false
            arg1: col:A
            arg2: c:B
        - multiply:
            name: percentage
            output: true
            arg1: tran:A_and_B_div
            arg2: 100
        - divide:
            name: reciprocal
            output: true
            arg2: 1
            arg1: tran:A_and_B_div
        - in:
            in_str: "a"
            arg: column:I
            output: true
        """
        original_col_length = len(data.columns)
        data, _ = parse_and_process_data(data, schema, test_yaml)
        assert "reciprocal" in data.columns
        assert "percentage" in data.columns
        assert "A_and_B_div" not in data.columns
        assert original_col_length + 3 == len(data.columns)
        assert data.iloc[:, -1:].columns[0][:3] == "in_"

    @pytest.mark.parametrize(
        "data_and_schema",
        [
            pytest.param(True, marks=integration_test),
            pytest.param(False, marks=unit_test),
        ],
        indirect=["data_and_schema"],
    )
    def test_multi_column_output_drop_cols(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests that multicolumn outputs are all dropped correctly."""
        data, schema = data_and_schema
        test_yaml = """
        Transformations:
        - OneHotEncode:
            name: ohe_I
            output: false
            arg: col:I
            values: [e,f,g]
        """
        data, _ = parse_and_process_data(data, schema, test_yaml)
        # Check no column with ohe_I in it exists
        for col in data.columns:
            assert not col.startswith("ohe_I")

    @unit_test
    def test_schema_invalid_columns(self) -> None:
        """Tests exception raised if referenced column doesn't exist."""
        test_yaml = """
        Transformations:
        - divide:
            name: A_and_B_div
            output: true
            arg1: col:col_that_doesntexist
            arg2: c:second_nonexistent_col
        """
        data = create_dataset()
        schema = BitfountSchema(DataFrameSource(data), table_name="test")
        parser = TransformationsParser()
        transformations, cols = parser.parse(test_yaml)
        processor = TransformationProcessor(transformations, schema.tables[0], cols)
        with pytest.raises(MissingColumnReferenceError) as tpe:
            processor.transform(data)
        assert tpe.value.errors == [
            f"Reference to non-existent column: {c}"
            for c in ("col_that_doesntexist", "second_nonexistent_col")
        ]

    @unit_test
    def test_schema_invalid_operation(self) -> None:
        """Tests exception raised if transformation operation invalid."""
        test_yaml = """
        Transformations:
        - divide:
            name: A_and_B_div
            output: false
            arg1: col:A
            arg2: c:I
        """
        data = create_dataset()
        schema = BitfountSchema(DataFrameSource(data), table_name="test")
        parser = TransformationsParser()
        transformations, cols = parser.parse(test_yaml)
        processor = TransformationProcessor(transformations, schema.tables[0], cols)
        original_col_length = len(data.columns)
        with pytest.raises(TransformationApplicationError):
            processor.transform(data)
        assert "A_and_B_div" not in data.columns
        assert original_col_length == len(data.columns)

    @unit_test
    def test_image_transformation(self) -> None:
        """Tests image transformation works correctly."""
        test_yaml = """
        Transformations:
        - Image:
            arg: col:col1
            output: True
            step: train
            transformations:
                - HorizontalFlip:
                    p: 0.5
                - RandomBrightnessContrast
        """
        parser = TransformationsParser()
        tfms, _ = parser.parse(test_yaml)
        proc = TransformationProcessor(tfms)
        image = np.array(Image.new("RGB", size=(50, 50), color=(100, 0, 255)))
        transformed_image = proc.batch_transform(image, step=DataSplit.TRAIN)
        assert isinstance(transformed_image, np.ndarray)
        assert transformed_image.shape == image.shape

    @unit_test
    def test_image_transformation_step_is_respected(self) -> None:
        """Tests that transformation is not applied if step does not match."""
        test_yaml = """
        Transformations:
        - Image:
            arg: col:col1
            output: True
            step: train
            transformations:
                - HorizontalFlip:
                    p: 0.5
                - RandomBrightnessContrast
        """
        parser = TransformationsParser()
        tfms, _ = parser.parse(test_yaml)
        proc = TransformationProcessor(tfms)
        image = np.array(Image.new("RGB", size=(50, 50), color=(100, 0, 255)))
        transformed_image = proc.batch_transform(image, step=DataSplit.VALIDATION)

        # Assert that the 'transformed' image is exactly the same
        np.testing.assert_array_equal(transformed_image, image)

    @unit_test
    def test_batch_transform_raises_value_error_with_non_batch_transformation(
        self,
    ) -> None:
        """Tests that `batch_tranform` can only be used with batch transformations."""
        test_yaml = """
        Transformations:
        - divide:
            name: A_and_B_div
            output: false
            arg1: col:A
            arg2: c:I
        """
        parser = TransformationsParser()
        tfms, _ = parser.parse(test_yaml)
        proc = TransformationProcessor(tfms)
        image = np.array(Image.new("RGB", size=(50, 50), color=(100, 0, 255)))
        with pytest.raises(InvalidBatchTransformationError):
            proc.batch_transform(image, step=DataSplit.TRAIN)

    @unit_test
    @pytest.mark.parametrize(
        "scalar",
        [pytest.param(2), pytest.param(0.1), pytest.param({"A": 0.2, "B": 10, "C": 4})],
    )
    def test_scalar_multiplication(
        self,
        data_and_schema: Tuple[pd.DataFrame, TableSchema],
        scalar: Union[int, float, Mapping[str, Union[int, float]]],
    ) -> None:
        """Tests the scalar multiplication is applied correctly."""
        data, schema = data_and_schema
        orig_data = data.copy()
        scalar_transform = ScalarMultiplicationDataTransformation(scalar=scalar)
        processor = TransformationProcessor([scalar_transform], schema)
        data = processor.transform(data)
        if isinstance(scalar, (int, float)):
            for feature in ["E", "F", "G", "H"]:
                assert (orig_data[feature] * scalar).to_list() == data[
                    feature
                ].to_list()
        else:
            for feature in ["A", "B", "C"]:
                assert (orig_data[feature] * scalar[feature]).to_list() == data[
                    feature
                ].to_list()

    @unit_test
    def test_scalar_multiplication_raises_error_non_existing_column(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the scalar multiplication fails if col doesn't exist."""
        scalar = {"X": 1.5, "Z": 0.2}
        data, schema = data_and_schema
        scalar_transform = ScalarMultiplicationDataTransformation(scalar=scalar)
        processor = TransformationProcessor([scalar_transform], schema)
        with pytest.raises(MissingColumnReferenceError) as tpe:
            processor.transform(data)
        assert (
            tpe.value.errors.sort()
            == [f"Reference to non-existent column: {c}" for c in scalar.keys()].sort()
        )

    @unit_test
    def test_scalar_multiplication_raises_non_numeric_column(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the scalar multiplication fails non-numeric column."""
        scalar = {"Date": 1.5}
        data, schema = data_and_schema
        scalar_transform = ScalarMultiplicationDataTransformation(scalar=scalar)
        processor = TransformationProcessor([scalar_transform], schema)
        with pytest.raises(TransformationApplicationError):
            processor.transform(data)

    @unit_test
    def test_scalar_multiplication_raises_error_wrong_scalar(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the scalar multiplication if scalar is an incorrect format."""
        scalar = [1, 2, 3]
        with pytest.raises(TransformationApplicationError):
            ScalarMultiplicationDataTransformation(scalar=scalar)  # type: ignore[arg-type] # Reason: incorrect assignment to check if error is raised. # noqa: B950

    @unit_test
    @pytest.mark.parametrize(
        "scalar",
        [pytest.param(2), pytest.param(0.1), pytest.param({"A": 0.2, "B": 10, "C": 4})],
    )
    def test_scalar_addition(
        self,
        data_and_schema: Tuple[pd.DataFrame, TableSchema],
        scalar: Union[int, float, Mapping[str, Union[int, float]]],
    ) -> None:
        """Tests the scalar addition is applied correctly."""
        data, schema = data_and_schema
        orig_data = data.copy()
        scalar_transform = ScalarAdditionDataTransformation(scalar=scalar)
        processor = TransformationProcessor([scalar_transform], schema)
        data = processor.transform(data)
        if isinstance(scalar, (int, float)):
            for feature in ["E", "F", "G", "H"]:
                assert (orig_data[feature] + scalar).to_list() == data[
                    feature
                ].to_list()
        else:
            for feature in ["A", "B", "C"]:
                assert (orig_data[feature] + scalar[feature]).to_list() == data[
                    feature
                ].to_list()

    @unit_test
    def test_scalar_addition_raises_error_non_existing_column(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the scalar addition fails if col doesn't exist."""
        scalar = {"X": 1.5, "Z": 0.2}
        data, schema = data_and_schema
        scalar_transform = ScalarAdditionDataTransformation(scalar=scalar)
        processor = TransformationProcessor([scalar_transform], schema)
        with pytest.raises(MissingColumnReferenceError) as tpe:
            processor.transform(data)
        assert (
            tpe.value.errors.sort()
            == [f"Reference to non-existent column: {c}" for c in scalar.keys()].sort()
        )

    @unit_test
    def test_scalar_addition_raises_error_wrong_scalar(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the scalar addition if scalar is an incorrect format."""
        scalar = [1, 2, 3]
        with pytest.raises(TransformationApplicationError):
            ScalarAdditionDataTransformation(
                scalar=scalar  # type: ignore[arg-type] # Reason: incorrect assignment to check if error is raised. # noqa: B950
            )

    @unit_test
    def test_scalar_addition_raises_non_numeric_column(
        self, data_and_schema: Tuple[pd.DataFrame, TableSchema]
    ) -> None:
        """Tests the scalar addition fails non-numeric column."""
        scalar = {"Date": 1.5}
        data, schema = data_and_schema
        scalar_transform = ScalarAdditionDataTransformation(scalar=scalar)
        processor = TransformationProcessor([scalar_transform], schema)
        with pytest.raises(TransformationApplicationError):
            processor.transform(data)


@unit_test
class TestTransformationProcessorError:
    """Tests for TransformationProcessorError exception."""

    def test_single_error_arg(self) -> None:
        """Tests creation of TransformationProcessorError from single error."""
        with pytest.raises(TransformationProcessorError) as tpe:
            raise TransformationProcessorError("test")
        assert tpe.value.errors == ["test"]

    def test_multiple_error_arg(self) -> None:
        """Tests creation of TransformationProcessorError with multiple errors."""
        with pytest.raises(TransformationProcessorError) as tpe:
            raise TransformationProcessorError(["test", "test2"])
        assert tpe.value.errors == ["test", "test2"]

    def test_str(self) -> None:
        """Tests string representation of TransformationProcessorError."""
        with pytest.raises(TransformationProcessorError) as tpe:
            raise TransformationProcessorError(["test", "test2"])
        assert str(tpe.value) == "Errors: \ntest\ntest2"
