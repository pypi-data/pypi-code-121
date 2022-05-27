"""Tests schema.py."""
import copy
from pathlib import Path
import re
from typing import Dict, List, MutableMapping, Optional, Union
from unittest.mock import Mock, PropertyMock, create_autospec

from _pytest.logging import LogCaptureFixture
from marshmallow import ValidationError
import numpy as np
import pandas as pd
from pandas.core.dtypes.common import pandas_dtype
from pandas.testing import assert_frame_equal
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy
import yaml

import bitfount
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.schema import (
    BitfountSchema,
    BitfountSchemaError,
    TableSchema,
    _TableSchemaMarshmallowMixIn,
)
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    SemanticType,
    _SemanticTypeValue,
)
from bitfount.data.utils import DatabaseConnection, _generate_dtypes_hash, _hash_str
from bitfount.types import _Dtypes, _JSONDict
from tests.utils import PytestRequest
from tests.utils.helper import (
    TABLE_NAME,
    create_dataset,
    get_warning_logs,
    integration_test,
    unit_test,
)

SCHEMA_DUMP_PATH: str = "schema_dump_test.yaml"


@fixture
def data() -> pd.DataFrame:
    """Returns dataset."""
    return create_dataset()


@fixture(params=["dataframe", "db", "db_multi_table", "db_query"])
def datasource(
    request: PytestRequest,
    data: pd.DataFrame,
    db_session: sqlalchemy.engine.base.Engine,
) -> _BaseSource:
    """Returns datasource."""
    datasource: _BaseSource
    if request.param == "db":
        db_conn = DatabaseConnection(db_session, table_names=["dummy_data"])
        datasource = DatabaseSource(db_conn, seed=420)
    elif request.param == "db_multi_table":
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        datasource = DatabaseSource(db_conn, seed=420)
    elif request.param == "db_query":
        db_conn = DatabaseConnection(db_session, query="SELECT * FROM dummy_data")
        datasource = DatabaseSource(db_conn, seed=420)
    elif request.param == "dataframe":
        datasource = DataFrameSource(data, seed=420)
    else:
        raise ValueError(
            "Supported Data Sources are : dataframe, db, db_multi_table and db_query."
        )

    return datasource


@fixture
def image_datasource() -> DataFrameSource:
    """Datasource with image_col for testing."""
    data = create_dataset(image=True)
    ds = DataFrameSource(data, image_col=["image"])
    ds.load_data()
    return ds


@fixture
def table_schema() -> TableSchema:
    """An EMPTY TableSchema object."""
    return TableSchema(name=TABLE_NAME)


@fixture
def schema() -> BitfountSchema:
    """An EMPTY BitfountSchema object."""
    return BitfountSchema()


@fixture
def table_schema_with_data(
    datasource: _BaseSource, table_schema: TableSchema
) -> TableSchema:
    """Schema with datasource already set."""
    if isinstance(datasource, DatabaseSource) and (
        table_names := datasource.table_names
    ):
        table_schema = TableSchema(name=table_names[0])
    table_schema.add_dataframe_features(datasource)
    return table_schema


@fixture
def schema_with_data(datasource: _BaseSource, schema: BitfountSchema) -> BitfountSchema:
    """Schema with datasource already set."""
    if isinstance(datasource, DatabaseSource) and (
        table_names := datasource.table_names
    ):
        schema.add_datasource_tables(datasource, table_name=table_names[0])
    else:
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
    return schema


@unit_test
class TestSchemaSerialization:
    """Tests we can save and load schema as yaml."""

    @fixture
    def empty_schema_hash(self) -> str:
        """The expected hash for a schema with no datasources."""
        empty_list: list = []
        return _hash_str(str(empty_list))

    @fixture
    def bitfount_version(self) -> str:
        """The bitfount version."""
        return bitfount.__version__

    @fixture
    def empty_schema_metadata(
        self, bitfount_version: str, empty_schema_hash: str
    ) -> Dict[str, str]:
        """The expected metadata for a schema with no datasources."""
        return {
            "bitfount_version": bitfount_version,
            "hash": empty_schema_hash,
            "schema_version": "1",
        }

    def test_schema_dump_load(
        self, datasource: _BaseSource, schema: BitfountSchema, tmp_path: Path
    ) -> None:
        """Tests dumping and loading data schema."""
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        file_path = tmp_path / SCHEMA_DUMP_PATH
        schema.dump(file_path)
        loaded_schema = BitfountSchema.load_from_file(file_path)

        assert (
            yaml.safe_load(schema.dumps())["tables"]
            == yaml.safe_load(loaded_schema.dumps())["tables"]
        )

    def test_multi_table_schema_dump_load(
        self,
        mock_engine: Mock,
        mock_pandas_read_sql_query: None,
        mocker: MockerFixture,
        schema: BitfountSchema,
        tmp_path: Path,
    ) -> None:
        """Tests dumping and loading multi-table schema."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        ds = DatabaseSource(db_conn, seed=420)
        mock_dtypes = create_dataset().dtypes.to_dict()
        mocker.patch.object(ds, "get_dtypes", return_value=mock_dtypes)
        ds._table_hashes.add(_generate_dtypes_hash(mock_dtypes))
        mocker.patch.object(
            ds,
            "get_values",
            side_effect=lambda x, table_name: {
                col: create_dataset()[col].unique() for col in x
            },
        )
        schema.add_datasource_tables(ds)
        assert schema.table_names == ["dummy_data", "dummy_data_2"]

        file_path = tmp_path / SCHEMA_DUMP_PATH
        schema.dump(file_path)
        loaded_schema = BitfountSchema.load_from_file(file_path)
        assert loaded_schema.table_names == ["dummy_data", "dummy_data_2"]
        assert (
            yaml.safe_load(schema.dumps())["tables"]
            == yaml.safe_load(loaded_schema.dumps())["tables"]
        )

    def test_dump_produces_metadata(
        self, bitfount_version: str, empty_schema_hash: str, schema: BitfountSchema
    ) -> None:
        """Tests that metadata is output in the schema dump."""
        dumped = schema.dumps()
        loaded_yaml = yaml.safe_load(dumped)
        assert loaded_yaml["metadata"] == {
            "hash": empty_schema_hash,
            "bitfount_version": bitfount_version,
            "schema_version": "1",
        }

    def test_load_works_without_metadata(
        self, datasource: _BaseSource, schema: BitfountSchema, tmp_path: Path
    ) -> None:
        """Tests loading works if metadata tag not present."""
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        dumped = schema.dumps()
        # Remove metadata from dumped schema and save to file
        loaded_yaml = yaml.safe_load(dumped)
        del loaded_yaml["metadata"]
        assert "metadata" not in loaded_yaml
        file_path = tmp_path / "schema.yaml"
        with open(file_path, "w") as f:
            yaml.dump(loaded_yaml, f)

        # Load as BitfountSchema
        loaded_schema = BitfountSchema.load_from_file(file_path)

        # Check orig_hash not set (outcome of metadata loading)
        assert loaded_schema._orig_hash is None

    def test_schema_dump_load_sorts_keys_alphabetically(
        self, datasource: _BaseSource, tmp_path: Path
    ) -> None:
        """Tests that key ordering is made alphabetical by dump and load."""
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        file_path = tmp_path / SCHEMA_DUMP_PATH
        schema.dump(file_path)
        loaded_schema = BitfountSchema.load_from_file(file_path)

        for table in schema.tables:
            for stype in table.features:
                semantic_type = SemanticType(stype)
                original_feature_names = table.get_feature_names(semantic_type)
                loaded_feature_names = loaded_schema.get_feature_names(
                    table.name, semantic_type
                )
                assert sorted(original_feature_names) == loaded_feature_names

    def test_schema_json_dump_has_correct_casing(
        self, empty_schema_metadata: Dict[str, str]
    ) -> None:
        """Tests camelCased output of JSON dump.

        We don't want to be changing the casing of fields that are from our dataset,
        i.e. feature names, categorical classes, but we do want python variable names
        to be camelCased so that they are consistent with the JSON format.
        """
        bf_schema = BitfountSchema()
        bf_schema.tables = [TableSchema(TABLE_NAME)]
        schema = bf_schema.tables[0]
        schema.features["continuous"] = {
            "snake_cased_name2": ContinuousRecord(
                "snake_cased_name2", pandas_dtype("float32")
            ),
            "camelCasedName2": ContinuousRecord(
                "camelCasedName2", pandas_dtype("float32")
            ),
        }

        record_with_encoder_one = CategoricalRecord(
            feature_name="snake_cased_name1", dtype=pd.StringDtype()
        )
        record_with_encoder_two = CategoricalRecord(
            feature_name="camelCasedName1", dtype=pd.StringDtype()
        )

        record_with_encoder_one.encoder.add_values(
            np.array(["these_are", "snake_cased"])
        )
        record_with_encoder_two.encoder.add_values(np.array(["theseAre", "camelCased"]))

        schema.features["categorical"] = {
            "snake_cased_name1": record_with_encoder_one,
            "camelCasedName1": record_with_encoder_two,
        }

        dumped_schema = bf_schema.dumps()
        expected_schema = yaml.dump(
            {
                "tables": [
                    {
                        "name": TABLE_NAME,
                        "description": None,
                        "features": [
                            {
                                "featureName": "camelCasedName1",
                                "description": None,
                                "dtype": "string",
                                "encoder": {
                                    "classes": {"camelCased": 0, "theseAre": 1}
                                },
                                "semanticType": "categorical",
                            },
                            {
                                "featureName": "camelCasedName2",
                                "description": None,
                                "dtype": "float32",
                                "semanticType": "continuous",
                            },
                            {
                                "featureName": "snake_cased_name1",
                                "description": None,
                                "dtype": "string",
                                "encoder": {
                                    "classes": {"snake_cased": 0, "these_are": 1}
                                },
                                "semanticType": "categorical",
                            },
                            {
                                "featureName": "snake_cased_name2",
                                "description": None,
                                "dtype": "float32",
                                "semanticType": "continuous",
                            },
                        ],
                    }
                ],
                "metadata": empty_schema_metadata,
            },
            sort_keys=False,
        )
        assert dumped_schema == expected_schema

    def test_schema_load_invalid_stype(
        self, datasource: _BaseSource, tmp_path: Path
    ) -> None:
        """Tests that semantic types must be predefined in the Enum."""
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        file_path = tmp_path / SCHEMA_DUMP_PATH
        schema.dump(file_path)

        # Read in the file
        with open(file_path, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("continuous", "not_real_stype")

        # Write the file out again
        with open(file_path, "w") as file:
            file.write(filedata)

        with pytest.raises(ValidationError, match="['Unknown field.']"):
            BitfountSchema.load_from_file(file_path)

    def test_schema_load_invalid_dtype(
        self, datasource: _BaseSource, tmp_path: Path
    ) -> None:
        """Tests schema load fails if invalid dtype.

        Tests that a custom error message is reported when an invalid dtype is
        provided to a ContinuousRecord.
        """
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)

        schema.tables[0].features["continuous"]["A"].dtype = "THIS_IS_NOT_A_VALID_DTYPE"

        file_path = tmp_path / SCHEMA_DUMP_PATH
        schema.dump(file_path)
        with pytest.raises(
            ValidationError,
            match="Continuous record `dtype` expected a valid np.dtype or a pandas"
            + " dtype but received: `THIS_IS_NOT_A_VALID_DTYPE`.",
        ):
            BitfountSchema.load_from_file(file_path)

    def test_schema_with_image_dump_load(
        self, image_datasource: DataFrameSource, schema: BitfountSchema, tmp_path: Path
    ) -> None:
        """Tests dumping and (re)loading a schema gives equal item."""
        file_path = tmp_path / SCHEMA_DUMP_PATH
        schema.add_datasource_tables(image_datasource, table_name=TABLE_NAME)
        schema.dump(file_path)
        loaded_schema = BitfountSchema.load_from_file(file_path)

        assert (
            yaml.safe_load(schema.dumps())["tables"]
            == yaml.safe_load(loaded_schema.dumps())["tables"]
        )

    def test_schema_split_features(self) -> None:
        """Tests the pre-load split_features function."""
        schema_json_dict = {
            "features": [
                {
                    "featureName": "TARGET",
                    "description": None,
                    "dtype": "int64",
                    "encoder": {"classes": {"0": 0, "1": 1}},
                    "semanticType": "categorical",
                },
                {
                    "featureName": "age",
                    "description": None,
                    "dtype": "float64",
                    "semanticType": "continuous",
                },
            ]
        }
        schema = _TableSchemaMarshmallowMixIn._Schema()

        # Check split_features splits features by stype
        schema_1 = schema.split_features(schema_json_dict)
        assert "categoricalFeatures" in schema_1.keys()
        assert "continuousFeatures" in schema_1.keys()

        # Check that on the second call, it just returns the data
        schema_after_2_loads = schema.split_features(schema_1)
        assert schema_after_2_loads == schema_1

        # Check that it raises error if no 'features' in the data.
        with pytest.raises(ValueError):
            schema.split_features({"data": "value"})


@unit_test
class TestTableSchema:
    """Tests TableSchema class."""

    def test_schema_add_datasource(
        self, datasource: _BaseSource, table_schema: TableSchema
    ) -> None:
        """Checks ability to add a dataset."""
        if isinstance(datasource, DatabaseSource):
            if table_names := datasource.table_names:
                table_schema = TableSchema(name=table_names[0])
        table_schema.add_dataframe_features(datasource)
        datasource.load_data()
        if not datasource.multi_table:
            assert len(table_schema.get_feature_names()) == len(datasource.data.columns)
        assert (
            "I" in table_schema.features["text"]
        )  # I's values are letters of alphabet
        assert (
            table_schema.features["categorical"]["M"].encoder.size == 2
        )  # M's values are boolean

    def test_schema_expand_dataframe_str(self, table_schema: TableSchema) -> None:
        """Checks we can add extend when columns have string types."""
        data1 = pd.DataFrame([["a", "b"], ["c", "d"]], columns=["A", "B"])
        data2 = pd.DataFrame([["a", "b"], ["c", "d"]], columns=["B", "C"])
        expect1 = pd.DataFrame(
            [["a", "b", "nan"], ["c", "d", "nan"]], columns=["A", "B", "C"]
        )
        expect2 = pd.DataFrame(
            [["a", "b", "nan"], ["c", "d", "nan"]], columns=["B", "C", "A"]
        )
        ds1 = DataFrameSource(data1)
        ds2 = DataFrameSource(data2)
        table_schema.add_dataframe_features(ds1)
        table_schema.add_dataframe_features(ds2)
        data1_exp = table_schema._expand_dataframe(data1)
        data2_exp = table_schema._expand_dataframe(data2)
        assert_frame_equal(data1_exp, expect1)
        assert_frame_equal(data2_exp, expect2)

    def test_schema_expand_dataframe_bool(self, table_schema: TableSchema) -> None:
        """Checks we can add extend when columns have bool types."""
        data1 = pd.DataFrame([[True, False], [True, False]], columns=["A", "B"])
        data2 = pd.DataFrame([[True, False], [True, False]], columns=["B", "C"])
        expect1 = pd.DataFrame(
            [[True, False, "nan"], [True, False, "nan"]],
            columns=["A", "B", "C"],
        )
        expect2 = pd.DataFrame(
            [[True, False, "nan"], [True, False, "nan"]],
            columns=["B", "C", "A"],
        )
        ds1 = DataFrameSource(data1)
        ds2 = DataFrameSource(data2)
        table_schema.add_dataframe_features(ds1)
        table_schema.add_dataframe_features(ds2)
        data1_exp = table_schema._expand_dataframe(data1)
        data2_exp = table_schema._expand_dataframe(data2)
        assert_frame_equal(data1_exp, expect1)
        assert_frame_equal(data2_exp, expect2)

    def test_schema_expand_dataframe_float(self, table_schema: TableSchema) -> None:
        """Checks we can add extend when columns have float types."""
        data1 = pd.DataFrame([[1.0, 2.0], [3.0, 4.0]], columns=["A", "B"])
        data2 = pd.DataFrame([[1.0, 2.0], [3.0, 4.0]], columns=["B", "C"])
        expect1 = pd.DataFrame([[1.0, 2.0, 0], [3.0, 4.0, 0]], columns=["A", "B", "C"])
        expect2 = pd.DataFrame([[1.0, 2.0, 0], [3.0, 4.0, 0]], columns=["B", "C", "A"])
        ds1 = DataFrameSource(data1)
        ds2 = DataFrameSource(data2)
        table_schema.add_dataframe_features(ds1)
        table_schema.add_dataframe_features(ds2)
        data1_exp = table_schema._expand_dataframe(data1)
        data2_exp = table_schema._expand_dataframe(data2)
        assert_frame_equal(data1_exp, expect1)
        assert_frame_equal(data2_exp, expect2)

    def test_schema_expand_dataframe_int(self, table_schema: TableSchema) -> None:
        """Checks we can add extend when columns have float types."""
        data1 = pd.DataFrame([[1, 2], [3, 4]], columns=["A", "B"])
        data2 = pd.DataFrame([[1, 2], [3, 4]], columns=["B", "C"])
        expect1 = pd.DataFrame([[1, 2, 0], [3, 4, 0]], columns=["A", "B", "C"])
        expect2 = pd.DataFrame([[1, 2, 0], [3, 4, 0]], columns=["B", "C", "A"])
        ds1 = DataFrameSource(data1)
        ds2 = DataFrameSource(data2)
        table_schema.add_dataframe_features(ds1)
        table_schema.add_dataframe_features(ds2)
        data1_exp = table_schema._expand_dataframe(data1)
        data2_exp = table_schema._expand_dataframe(data2)
        assert_frame_equal(data1_exp, expect1)
        assert_frame_equal(data2_exp, expect2)

    def test_schema_add_datasource_with_image(
        self, image_datasource: DataFrameSource, table_schema: TableSchema
    ) -> None:
        """Tests add_dataframe_features works correctly."""
        table_schema.add_dataframe_features(
            image_datasource, force_stype={"image": ["image"]}
        )
        assert len(table_schema.get_feature_names()) == len(
            image_datasource.data.columns
        )
        assert table_schema.features["categorical"]["M"].encoder.size == 2
        assert list(table_schema.features["image"].keys()) == ["image"]
        image_feature = table_schema.features["image"]["image"]
        assert dict(image_feature.dimensions) == {(50, 50): 4000}
        assert "RGB" in image_feature.modes
        assert "L" in image_feature.modes
        assert dict(image_feature.formats) == {"PNG": 4000}

    def test_schema_add_datasource_without_force_stype_doesnt_contain_image_col(
        self,
        image_datasource: DataFrameSource,
        table_schema: TableSchema,
    ) -> None:
        """Tests that image col is not added to images."""
        table_schema.add_dataframe_features(image_datasource)
        assert "image" not in table_schema.features

    def test_force_stypes(
        self, image_datasource: DataFrameSource, table_schema: TableSchema
    ) -> None:
        """Tests that all force_stypes are added to schema."""
        force_stype: MutableMapping[_SemanticTypeValue, List[str]]
        force_stype = {
            "categorical": ["M", "J"],
            "continuous": ["A"],
            "text": ["N"],
            "image": ["image"],
            "blah": ["B"],  # type: ignore[dict-item] # Reason: see below.
        }
        # Added the 'blah' dict key to check that if a value is given a semantic type
        # which we don't support, it defaults to the semantic value based
        # on dtype.
        table_schema.add_dataframe_features(image_datasource, force_stype=force_stype)
        assert "M" in table_schema.features["categorical"]
        assert "J" in table_schema.features["categorical"]
        assert "A" in table_schema.features["continuous"]
        assert "N" in table_schema.features["text"]
        assert "B" in table_schema.features["continuous"]
        assert "image" in table_schema.features["image"]

    def test_stype_images(self, table_schema: TableSchema) -> None:
        """Tests multiple images added to schema."""
        data = create_dataset(classification=False, multiimage=True, img_size=2)
        ds = DataFrameSource(data[["image1", "image2", "TARGET"]])
        ds.load_data()
        force_stype: MutableMapping[_SemanticTypeValue, List[str]]
        force_stype = {"image": ["image1", "image2"], "text": ["TARGET"]}
        table_schema.add_dataframe_features(ds, force_stype=force_stype)
        assert "image1" in table_schema.features["image"]
        assert "image2" in table_schema.features["image"]
        assert "TARGET" in table_schema.features["text"]

    def test_encode_dataframe(self, table_schema: TableSchema) -> None:
        """Tests schema encodes dataframe correctly."""
        data = pd.DataFrame([["a", "b"], ["c", "d"]], columns=["A", "B"])
        ds = DataFrameSource(data)
        table_schema.add_dataframe_features(ds, force_stype={"categorical": ["A", "B"]})
        expect = pd.DataFrame(
            [
                [
                    table_schema.features["categorical"]["A"].encoder.classes["a"],
                    table_schema.features["categorical"]["B"].encoder.classes["b"],
                ],
                [
                    table_schema.features["categorical"]["A"].encoder.classes["c"],
                    table_schema.features["categorical"]["B"].encoder.classes["d"],
                ],
            ],
            columns=["A", "B"],
        )
        data_exp = table_schema._encode_dataframe(data)
        assert_frame_equal(data_exp, expect)

    def test_reduce_dataframe(self, table_schema: TableSchema) -> None:
        """Tests reduce_dataframe removes appropriate columns."""
        data = pd.DataFrame([["a", "b"], ["c", "d"]], columns=["A", "B"])
        ds = DataFrameSource(data)
        ds.load_data()
        table_schema.add_dataframe_features(ds)
        data2 = pd.DataFrame(
            [["a", "b", "c"], ["d", "e", "f"]], columns=["A", "B", "C"]
        )
        expect = pd.DataFrame([["a", "b"], ["d", "e"]], columns=["A", "B"])
        data_exp = table_schema._reduce_dataframe(data2)
        data_exp = data_exp.reindex(sorted(data_exp.columns), axis=1)
        assert_frame_equal(data_exp, expect)

    def test_apply_types(self, table_schema: TableSchema) -> None:
        """Tests apply_types changes types of columns appropriately."""
        data = pd.DataFrame([[1.1, 2.2], [3.3, 4.4]], columns=["A", "B"])
        ds = DataFrameSource(data)
        table_schema.add_dataframe_features(ds)
        data2 = pd.DataFrame([[5, 6], [7, 8]], columns=["A", "B"])
        expect = pd.DataFrame(
            [[5.0, 6.0], [7.0, 8.0]], columns=["A", "B"]
        ).convert_dtypes(convert_integer=False)
        data_exp = table_schema._apply_types(data2)
        assert_frame_equal(data_exp, expect)

    def test_categorical_feature_sizes_with_no_ignore_cols(
        self, table_schema: TableSchema
    ) -> None:
        """Schema returns all categorical sizes if no ignore_cols provided."""
        data = pd.DataFrame([[True, False], [False, True]], columns=["A", "B"])
        ds = DataFrameSource(data)
        table_schema.add_dataframe_features(ds)
        assert table_schema.get_categorical_feature_sizes() == [2, 2]

    def test_categorical_feature_sizes_with_ignore_cols(
        self, table_schema: TableSchema
    ) -> None:
        """Schema returns correct categorical sizes when ignore_cols is categorical."""
        data = pd.DataFrame([[True, False], [False, True]], columns=["A", "B"])
        ds = DataFrameSource(data)
        table_schema.add_dataframe_features(ds)
        assert table_schema.get_categorical_feature_sizes(ignore_cols="A") == [2]

    def test_get_categorical_feature_size_raises_value_error_when_there_are_no_categorical_features(  # noqa: B950
        self, table_schema: TableSchema
    ) -> None:
        """Tests that `get_categorical_feature_size` raises a ValueError appropriately.

        When there are no categorical features.
        """
        with pytest.raises(ValueError, match="No categorical features."):
            table_schema.get_categorical_feature_size("feature")

    def test_get_categorical_feature_size_raises_value_error_when_missing(
        self, table_schema: TableSchema
    ) -> None:
        """Tests that `get_categorical_feature_size` raises a ValueError appropriately.

        When it is missing from the list of categorical features.
        """
        table_schema.features["categorical"] = {
            "feature_1": Mock(),
            "feature_2": Mock(),
        }
        with pytest.raises(
            ValueError,
            match="missing_feature feature not found in categorical features.",
        ):
            table_schema.get_categorical_feature_size("missing_feature")

    def test_get_categorical_feature_with_list(self, table_schema: TableSchema) -> None:
        """Tests that `get_categorical_feature_size` works properly with a list.

        If a list of features is provided, we only return the size of the encoder for
        the first element.
        """
        table_schema.features["categorical"] = {
            "feature_1": Mock(encoder=Mock(size=5)),
            "feature_2": Mock(),
        }
        assert (
            table_schema.get_categorical_feature_size(["feature_1", "feature_2"]) == 5
        )

    @pytest.mark.parametrize(
        argnames="ignore_cols",
        argvalues=(
            pytest.param(None, id="no ignore_cols"),
            pytest.param("A", id="string ignore_cols"),
            pytest.param(["A"], id="list ignore_cols"),
        ),
    )
    def test_get_num_categorical(
        self,
        ignore_cols: Optional[Union[str, List[str]]],
        table_schema: TableSchema,
    ) -> None:
        """Tests get_num_categorical for different types of ignore_cols."""
        # Create schema with categorical data columns
        data = pd.DataFrame([[True, False], [False, True]], columns=["A", "B"])
        ds = DataFrameSource(data)
        ds.load_data()
        table_schema.add_dataframe_features(ds)

        num_categorical = table_schema.get_num_categorical(ignore_cols)

        if ignore_cols:
            # Only "B"
            assert num_categorical == 1
        else:
            # Both "A" and "B"
            assert num_categorical == 2

    @pytest.mark.parametrize(
        argnames="ignore_cols",
        argvalues=(
            pytest.param(None, id="no ignore_cols"),
            pytest.param("A", id="string ignore_cols"),
            pytest.param(["A"], id="list ignore_cols"),
        ),
    )
    def test_get_num_continuous(
        self,
        ignore_cols: Optional[Union[str, List[str]]],
        table_schema: TableSchema,
    ) -> None:
        """Tests get_num_continuous for different types of ignore_cols."""
        # Create schema with continuous data columns
        data = pd.DataFrame([[1, 2], [3, 4]], columns=["A", "B"])
        ds = DataFrameSource(data)
        ds.load_data()
        table_schema.add_dataframe_features(ds)

        num_continuous = table_schema.get_num_continuous(ignore_cols)

        if ignore_cols:
            # Only "B"
            assert num_continuous == 1
        else:
            # Both "A" and "B"
            assert num_continuous == 2

    def test__eq__passes_same_item(self, table_schema: TableSchema) -> None:
        """Test __eq__ passes when items are exact same."""
        assert table_schema == table_schema

    def test__eq__passes_same_features(
        self, table_schema_with_data: TableSchema
    ) -> None:
        """Test __eq__ passes when items have same features and types."""
        other_schema = copy.deepcopy(table_schema_with_data)

        # Check unique objects
        assert table_schema_with_data is not other_schema
        # Check still viewed as equal
        assert table_schema_with_data == other_schema

    def test__eq__fails_not_schema(self, table_schema: TableSchema) -> None:
        """Test __eq__ fails when other is not a TableSchema."""
        assert table_schema != object()

    def test__eq__fails_diff_feature_names(
        self, table_schema_with_data: TableSchema
    ) -> None:
        """Test __eq__ fails when feature names differ."""
        other_schema = copy.deepcopy(table_schema_with_data)

        # Remove a categorical feature
        cat_features = other_schema.features["categorical"]
        cat_features.pop(list(cat_features.keys())[0])

        assert table_schema_with_data != other_schema

    def test__eq__fails_diff_feature_dtypes(
        self, table_schema_with_data: TableSchema
    ) -> None:
        """Test __eq__ fails when feature dtypes differ."""
        other_schema = copy.deepcopy(table_schema_with_data)

        # Extract and replace dtype of a categorical feature
        cat_features = other_schema.features["categorical"]
        record = list(cat_features.values())[0]
        if record.dtype is not np.uint8:
            record.dtype = np.uint8
        else:
            record.dtype = np.uint16

        assert table_schema_with_data != other_schema

    def test__eq__fails_diff_feature_stypes(
        self, table_schema_with_data: TableSchema
    ) -> None:
        """Test __eq__ fails when feature stypes differ."""
        other_schema = copy.deepcopy(table_schema_with_data)

        # Extract and replace stype of a categorical feature
        cat_features = other_schema.features["categorical"]
        feature_name, record = list(cat_features.items())[0]
        # Create mock record with a different stype
        mock_record = create_autospec(record)
        type(mock_record).semantic_type = PropertyMock(return_value="diff_stype")
        # Set as feature
        cat_features[feature_name] = mock_record

        assert table_schema_with_data != other_schema


@unit_test
class TestTableSchemaSplittingByDtype:
    """Tests the dtype_based_stype_split static method on TableSchema."""

    # qlalchemy.sql.sqltypes.DATE

    @pytest.mark.parametrize(
        "data",
        [
            # csv / pandas
            pd.DataFrame([1.0, 2.0], columns=["A"], dtype=np.float32).dtypes.to_dict(),
            # database
            {"A": float},
        ],
    )
    def test_float_dtype(self, data: _Dtypes) -> None:
        """Tests that floats are given the correct semantic type."""
        types = TableSchema._dtype_based_stype_split(data)
        assert types == {SemanticType.CONTINUOUS: ["A"]}

    @pytest.mark.parametrize(
        "data",
        [
            # csv / pandas
            pd.DataFrame([1, 2], columns=["A"], dtype=np.int32).dtypes.to_dict(),
            # database
            {"A": int},
        ],
    )
    def test_int_dtype(self, data: _JSONDict) -> None:
        """Tests that integers are given the correct semantic type."""
        types = TableSchema._dtype_based_stype_split(data)
        assert types == {SemanticType.CONTINUOUS: ["A"]}

    @pytest.mark.parametrize(
        "data",
        [
            # csv / pandas
            pd.DataFrame(["1", "2"], columns=["A"]).convert_dtypes().dtypes.to_dict(),
            # database
            {"A": str},
        ],
    )
    def test_str_dtype(self, data: _Dtypes) -> None:
        """Tests that strings are given the correct semantic type."""
        types = TableSchema._dtype_based_stype_split(data)
        assert types == {SemanticType.TEXT: ["A"]}

    @pytest.mark.parametrize(
        "data",
        [
            # csv / pandas
            pd.DataFrame([True, False], columns=["A"]).dtypes.to_dict(),
            # database
            {"A": bool},
        ],
    )
    def test_bool_dtype(self, data: _Dtypes) -> None:
        """Tests that booleans are given the correct semantic type."""
        types = TableSchema._dtype_based_stype_split(data)
        assert types == {SemanticType.CATEGORICAL: ["A"]}

    def test_object_dtype(self) -> None:
        """Tests that objects are given the correct semantic type."""

        class ComplexObject:
            ...

        data = pd.DataFrame([ComplexObject(), ComplexObject()], columns=["A"])
        types = TableSchema._dtype_based_stype_split(data.dtypes.to_dict())
        assert types == {SemanticType.CATEGORICAL: ["A"]}


class TestBitfountSchema:
    """Tests for the BitfountSchema class."""

    @unit_test
    def test_schema_not_frozen_when_created(self, schema: BitfountSchema) -> None:
        """Test that a newly created schema is not frozen."""
        assert schema._frozen is False

    @unit_test
    def test_schema_freeze(self, schema: BitfountSchema) -> None:
        """Test that BitfountSchema.freeze() freezes."""
        schema.freeze()
        assert schema._frozen is True

    @unit_test
    def test_schema_unfreeze(self, schema: BitfountSchema) -> None:
        """Test that BitfountSchema.unfreeze() unfreezes."""
        schema.freeze()
        assert schema._frozen is True
        schema.unfreeze()
        assert schema._frozen is False

    @unit_test
    def test_datasource_cannot_be_added_when_frozen(
        self, datasource: _BaseSource, schema: BitfountSchema
    ) -> None:
        """Tests that add_datasource_tables() fails when the schema is frozen."""
        schema.freeze()
        with pytest.raises(
            BitfountSchemaError,
            match=re.escape("This schema is frozen. No more datasources can be added."),
        ):
            schema.add_datasource_tables(datasource, table_name=TABLE_NAME)

    @unit_test
    def test_hash(self, schema: BitfountSchema) -> None:
        """Tests that hash generation works."""
        schema._datasource_hashes = set(["world", "hello"])

        # Should sort the stored "hashes"
        assert schema.hash == _hash_str(str(sorted(set(["hello", "world"]))))

    @unit_test
    def test_freeze_raises_exception_if_hash_mismatch(
        self, schema: BitfountSchema
    ) -> None:
        """Tests that freeze raises an exception if previous hash doesn't match."""
        schema._orig_hash = "not_the_same_hash"
        with pytest.raises(
            BitfountSchemaError,
            match=re.escape(
                "This schema was generated against a different set of datasources "
                "and is incompatible with those selected. This may be due to "
                "changing column names or types. Please generate a new schema."
            ),
        ):
            schema.freeze()

    @unit_test
    def test_add_datasource_tables_requires_table_name_for_single_table_datasource(
        self, datasource: _BaseSource, schema: BitfountSchema
    ) -> None:
        """Tests that add_datasource_tables raises a ValueError.

        If a single table datasource is passed, the table name must be specified.
        """
        if not datasource.multi_table:
            with pytest.raises(
                ValueError,
                match="Must provide a table name for single table datasources.",
            ):
                schema.add_datasource_tables(datasource)

    @integration_test
    def test_add_datasource_tables_with_multi_table_datasource(
        self,
        data: pd.DataFrame,
        db_session: sqlalchemy.engine.base.Engine,
        schema: BitfountSchema,
    ) -> None:
        """Tests that add_datasource_tables works with a multi-table datasource."""
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        schema.add_datasource_tables(
            ds,
            force_stypes={
                "dummy_data": {"text": ["Date"]},
                "dummy_data_2": {"text": ["Date"]},
            },
        )
        assert len(schema.tables) == 2
        assert schema.table_names == ["dummy_data", "dummy_data_2"]
        for table_schema in schema.tables:
            assert table_schema.features is not None
            assert len(table_schema.get_feature_names()) == len(data.columns)

    @unit_test
    def test_mock_add_datasource_tables_with_multi_table_datasource(
        self,
        data: pd.DataFrame,
        mock_engine: Mock,
        mock_pandas_read_sql_query: None,
        mocker: MockerFixture,
        schema: BitfountSchema,
    ) -> None:
        """Tests that add_datasource_tables works with a multi-table datasource."""
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)

        mock_dtypes = create_dataset().dtypes.to_dict()
        mocker.patch.object(ds, "get_dtypes", return_value=mock_dtypes)
        ds._table_hashes.add(_generate_dtypes_hash(mock_dtypes))

        mocker.patch.object(
            ds,
            "get_values",
            side_effect=lambda x, table_name: {
                col: create_dataset()[col].unique() for col in x
            },
        )

        schema.add_datasource_tables(ds)
        assert len(schema.tables) == 2
        assert schema.table_names == ["dummy_data", "dummy_data_2"]
        for table_schema in schema.tables:
            assert table_schema.features is not None
            assert len(table_schema.get_feature_names()) == len(data.columns)

    @unit_test
    def test_mock_add_datasource_tables_with_multi_table_datasource_table_name_warning(
        self,
        caplog: LogCaptureFixture,
        mock_engine: Mock,
        mock_pandas_read_sql_query: None,
        mocker: MockerFixture,
        schema: BitfountSchema,
    ) -> None:
        """Tests that add_datasource_tables works with a multi-table datasource."""
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)

        mock_dtypes = create_dataset().dtypes.to_dict()
        mocker.patch.object(ds, "get_dtypes", return_value=mock_dtypes)
        ds._table_hashes.add(_generate_dtypes_hash(mock_dtypes))

        mocker.patch.object(
            ds,
            "get_values",
            side_effect=lambda x, table_name: {
                col: create_dataset()[col].unique() for col in x
            },
        )

        schema.add_datasource_tables(ds, table_name="this_should_be_ignored")
        assert len(schema.tables) == 2
        assert schema.table_names == ["dummy_data", "dummy_data_2"]
        warning_logs = get_warning_logs(caplog)
        assert (
            "Ignoring table_name argument for multi-table datasource." in warning_logs
        )

    @unit_test
    def test_add_datasource_tables_adds_to_hash_list(
        self, datasource: _BaseSource, mocker: MockerFixture, schema: BitfountSchema
    ) -> None:
        """Checks add_datasource_tables() adds to hash list.

        Each added datasource needs to be recorded, so we use the hash list to
        achieve this.
        """
        # Mock out datasource.hash
        mock_hash = PropertyMock(return_value="datasource_hash")
        mocker.patch.object(_BaseSource, "hash", mock_hash)

        assert schema._datasource_hashes == set()

        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)

        assert schema._datasource_hashes == set(["datasource_hash"])
        mock_hash.assert_called_once()

    @unit_test
    def test_get_table_schema(self, schema_with_data: BitfountSchema) -> None:
        """Tests that get_table_schema() returns the correct schema."""
        table_name = schema_with_data.table_names[0]
        assert (
            schema_with_data.get_table_schema(table_name) == schema_with_data.tables[0]
        )

    @unit_test
    def test_get_table_schema_raises_error_if_schema_not_found(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Tests that get_table_schema() raises an error if schema not found."""
        with pytest.raises(
            BitfountSchemaError, match="Table Not_a_table not found in schema."
        ):
            schema_with_data.get_table_schema("Not_a_table")

    @unit_test
    def test_get_feature_names(self, schema_with_data: BitfountSchema) -> None:
        """Test that get_feature_names is a wrapper around table schema."""
        table_name = schema_with_data.table_names[0]
        assert (
            schema_with_data.get_feature_names(table_name)
            == schema_with_data.tables[0].get_feature_names()
        )

    @unit_test
    def test_get_categorical_feature_sizes(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test that get_categorical_feature_sizes is a wrapper around table schema."""
        table_name = schema_with_data.table_names[0]
        assert (
            schema_with_data.get_categorical_feature_sizes(table_name)
            == schema_with_data.tables[0].get_categorical_feature_sizes()
        )

    @unit_test
    def test_get_categorical_feature_size(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test that get_categorical_feature_size is a wrapper around table schema."""
        table_name = schema_with_data.table_names[0]
        assert schema_with_data.get_categorical_feature_size(
            table_name, "Date"
        ) == schema_with_data.tables[0].get_categorical_feature_size("Date")

    @unit_test
    def test_empty_schema_cannot_be_applied(
        self, data: pd.DataFrame, schema: BitfountSchema
    ) -> None:
        """Tests that applying an empty schema raises an error."""
        with pytest.raises(
            BitfountSchemaError,
            match="No tables in schema.",
        ):
            schema.apply(data)

    @unit_test
    def test_multi_table_schema_cannot_be_applied_to_single_table_data(
        self, data: pd.DataFrame, schema_with_data: BitfountSchema
    ) -> None:
        """Tests that applying a multi-table schema to single table data errors."""
        schema_with_data.tables.append(schema_with_data.tables[0])
        with pytest.raises(
            BitfountSchemaError,
            match="Can't apply a multi-table schema to a single dataframe.",
        ):
            schema_with_data.apply(data)

    @unit_test
    def test_single_table_schema_apply_method_applies_schema(
        self, data: pd.DataFrame, schema: BitfountSchema
    ) -> None:
        """Tests that apply() applies the schema to the data."""
        mock_table_schema = Mock(spec=TableSchema)
        schema.tables = [mock_table_schema]
        schema.apply(data)
        mock_table_schema.apply.assert_called_once()

    @unit_test
    def test__eq__passes_same_item(self, schema: BitfountSchema) -> None:
        """Test __eq__ passes when items are exact same."""
        assert schema == schema

    @unit_test
    def test__eq__passes_same_features(self, schema_with_data: BitfountSchema) -> None:
        """Test __eq__ passes when items have same features and types."""
        other_schema = copy.deepcopy(schema_with_data)

        # Check unique objects
        assert schema_with_data is not other_schema
        # Check still viewed as equal
        assert schema_with_data == other_schema

    @unit_test
    def test__eq__fails_not_schema(self, schema: BitfountSchema) -> None:
        """Test __eq__ fails when other is not a BitfountSchema."""
        assert schema != object()

    @unit_test
    def test__eq__fails_diff_number_of_tables(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test __eq__ fails when number of tables differ."""
        other_schema = copy.deepcopy(schema_with_data)
        other_schema.tables.append(other_schema.tables[0])

        assert schema_with_data != other_schema

    @unit_test
    def test__eq__fails_diff_table_names(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test __eq__ fails when table names differ."""
        other_schema = copy.deepcopy(schema_with_data)
        other_schema.tables[0].name = "other_name"

        assert schema_with_data != other_schema

    @unit_test
    def test__eq__fails_diff_feature_names(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test __eq__ fails when feature names differ."""
        other_schema = copy.deepcopy(schema_with_data)

        # Remove a categorical feature
        cat_features = other_schema.tables[0].features["categorical"]
        cat_features.pop(list(cat_features.keys())[0])

        assert schema_with_data != other_schema

    @unit_test
    def test__eq__fails_diff_feature_dtypes(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test __eq__ fails when feature dtypes differ."""
        other_schema = copy.deepcopy(schema_with_data)

        # Extract and replace dtype of a categorical feature
        cat_features = other_schema.tables[0].features["categorical"]
        record = list(cat_features.values())[0]
        if record.dtype is not np.uint8:
            record.dtype = np.uint8
        else:
            record.dtype = np.uint16

        assert schema_with_data != other_schema

    @unit_test
    def test__eq__fails_diff_feature_stypes(
        self, schema_with_data: BitfountSchema
    ) -> None:
        """Test __eq__ fails when feature stypes differ."""
        other_schema = copy.deepcopy(schema_with_data)

        # Extract and replace stype of a categorical feature
        cat_features = other_schema.tables[0].features["categorical"]
        feature_name, record = list(cat_features.items())[0]
        # Create mock record with a different stype
        mock_record = create_autospec(record)
        type(mock_record).semantic_type = PropertyMock(return_value="diff_stype")
        # Set as feature
        cat_features[feature_name] = mock_record

        assert schema_with_data != other_schema
