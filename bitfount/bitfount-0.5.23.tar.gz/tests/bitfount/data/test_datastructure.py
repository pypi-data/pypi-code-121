"""Tests datastructure.py."""
from typing import Dict, List, Union
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest
from pytest_asyncio import fixture

from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DEFAULT_IMAGE_TRANSFORMATIONS, DataStructure
from bitfount.data.exceptions import DataStructureError
from bitfount.data.types import DataSplit, SchemaOverrideMapping
from bitfount.runners.config_schemas import (
    DataStructureAssignConfig,
    DataStructureSelectConfig,
    DataStructureTableConfig,
    DataStructureTransformConfig,
)
from bitfount.transformations.batch_operations import ImageTransformation
from bitfount.types import _StrAnyDict
from tests.utils.helper import TABLE_NAME, unit_test


@unit_test
class TestDataStructure:
    """Tests DataStructure class."""

    @fixture
    def query(self) -> str:
        """Query fixture."""
        return "SELECT * from TABLE"

    def test_transformed_columns_added_to_datastructure(self) -> None:
        """Tests that the transformed columns are added to our datastructure."""
        dataset: List[Dict[str, _StrAnyDict]] = [
            {"convert_to": {"type": "string", "col": "TARGET"}},
            {"normalizedata": {"col": ["A", "B"], "keep_original": "A"}},
        ]
        batch = [{"image": {"arg": "col_1", "output": True}}]
        datastructure = DataStructure(
            target="TARGET",
            dataset_transforms=dataset,
            batch_transforms=batch,
            selected_cols=["A", "B", "C", "image"],
            table=TABLE_NAME,
        )
        assert set(datastructure.ignore_cols) == set(["B"])
        assert set(datastructure.selected_cols) == set(
            ["A", "A_normalizedata", "B_normalizedata", "C", "image"]
        )

    def test_create_datastructure_from_config(self) -> None:
        """Tests that the datastructure gets the right args fom configs."""
        select = DataStructureSelectConfig(
            include=["TARGET", "weights", "Col1", "image"]
        )
        assign = DataStructureAssignConfig(
            target="TARGET",
            loss_weights_col="weights",
            ignore_classes_col="ignore_classes",
        )
        transform = DataStructureTransformConfig(
            dataset=[{"convert_to": {"type": "string", "col": "TARGET"}}],
            batch=[{"crop": {"col": ["image"], "keep_original": "image"}}],
        )
        table_config = DataStructureTableConfig(table=TABLE_NAME)
        ds = DataStructure.create_datastructure(
            select=select,
            transform=transform,
            assign=assign,
            table_config=table_config,
        )
        assert ds.target == "TARGET"
        assert ds.ignore_cols == []
        assert set(ds.selected_cols) == set(["TARGET", "weights", "Col1", "image"])
        assert ds.loss_weights_col == "weights"
        assert ds.ignore_classes_col == "ignore_classes"
        assert ds.batch_transforms == [
            {"crop": {"col": ["image"], "keep_original": "image"}}
        ]
        assert ds.dataset_transforms == [
            {"convert_to": {"type": "string", "col": "TARGET"}}
        ]

    def test_create_datastructure_select_config_raises_error(self) -> None:
        """Tests that the providing both include and exclude cols raises error."""
        select = DataStructureSelectConfig(
            include=["TARGET", "weights", "multihead_col", "Col1"],
            exclude=["Col2", "Col3"],
        )
        transform = DataStructureTransformConfig()
        assign = DataStructureAssignConfig(target="TARGET")
        table_config = DataStructureTableConfig(table=TABLE_NAME)
        with pytest.raises(DataStructureError):
            DataStructure.create_datastructure(
                select=select,
                transform=transform,
                assign=assign,
                table_config=table_config,
            )

    def test_get_batch_transformations(self) -> None:
        """Tests `get_batch_transformations` method."""
        batch = [
            {
                "image": {
                    "step": "train",
                    "output": True,
                    "arg": "col1",
                    "transformations": ["RandomBrightnessContrast"],
                }
            }
        ]
        ds = DataStructure(
            target="TARGET",
            batch_transforms=batch,
            selected_cols=["A", "B", "C", "image"],
            table=TABLE_NAME,
        )
        tfms = ds.get_batch_transformations()
        assert tfms is not None
        assert len(tfms) == 1
        assert isinstance(tfms[0], ImageTransformation)

    def test_setting_default_image_transformations(self) -> None:
        """Tests that default batch transformations are set if not provided."""
        ds = DataStructure(
            target="TARGET",
            selected_cols=["A", "B", "C", "image"],
            image_cols=["image"],
            table=TABLE_NAME,
        )
        assert ds.batch_transforms is not None
        assert ds.batch_transforms == [
            {
                "Image": {
                    "arg": "image",
                    "output": True,
                    "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                    "step": "train",
                }
            },
            {
                "Image": {
                    "arg": "image",
                    "output": True,
                    "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                    "step": "validation",
                }
            },
            {
                "Image": {
                    "arg": "image",
                    "output": True,
                    "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                    "step": "test",
                }
            },
        ]

    def test_get_dataset_transformations_with_default_batch_transformations(
        self,
    ) -> None:
        """Tests that the default batch transformations are loaded correctly."""
        ds = DataStructure(
            target="TARGET",
            selected_cols=["A", "B", "C", "image"],
            image_cols=["image"],
            table=TABLE_NAME,
        )
        tfms = ds.get_batch_transformations()
        assert tfms is not None
        assert len(tfms) == 3
        for tfm, split in zip(tfms, DataSplit):
            assert isinstance(tfm, ImageTransformation)
            assert tfm.step == split

    def test_empty_batch_transformations(self) -> None:
        """Tests that batch transformations can be an empty list.

        Tests that if an empty list is explicitly provided and there are no image
        transformations, then the batch transformations stay empty.
        """
        ds = DataStructure(
            target="TARGET",
            selected_cols=["A", "B", "C", "image"],
            batch_transforms=[],
            table=TABLE_NAME,
        )
        assert ds.batch_transforms == []
        assert ds.get_batch_transformations() == []

    def test_get_table_name_with_single_table_datastructure(self) -> None:
        """Tests that the table name is returned correctly."""
        ds = DataStructure(
            target="TARGET",
            table=TABLE_NAME,
        )
        assert ds.get_table_name() == TABLE_NAME

    def test_get_table_name_with_multi_pod_datastructure(self) -> None:
        """Tests that the table name is returned correctly."""
        ds = DataStructure(
            target="TARGET",
            table={"pod1": "pod1_table", "pod2": "pod2_table"},
        )
        assert ds.get_table_name("pod1") == "pod1_table"

    def test_get_table_name_with_multi_pod_datastructure_raises_value_error(
        self,
    ) -> None:
        """Tests that the `get_table_name` method raises a ValueError."""
        ds = DataStructure(
            target="TARGET",
            table={"pod1": "pod1_table", "pod2": "pod2_table"},
        )
        with pytest.raises(
            ValueError, match="No pod identifier provided for multi-pod datastructure."
        ):
            ds.get_table_name()

    @pytest.mark.parametrize(
        "query", ["SELECT * FROM blah", {"pod1": "SELECT * FROM blah"}]
    )
    def test_get_table_schema_query(
        self, mocker: Mock, query: Union[str, dict]
    ) -> None:
        """Test get_table_schema with query."""
        mock_override_schema = mocker.patch.object(DataStructure, "_override_schema")
        mock_datasource = MagicMock(spec=DatabaseSource, query="SELECT * FROM table")
        mock_datasource.__len__.return_value = 1000
        pod_id = "pod1"

        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
            "continuous": ["col2"],
        }

        pod_schema_override = {pod_id: schema_override}

        ds = DataStructure(
            target="TARGET", query=query, schema_types_override=pod_schema_override
        )
        ds.get_table_schema(
            schema=Mock(), pod_identifier=pod_id, datasource=mock_datasource
        )

        mock_override_schema.assert_called_once()

    def test_get_pod_identifiers_with_single_table_datastructure(self) -> None:
        """Tests that `get_pod_identifiers` returns None if there are no pods."""
        ds = DataStructure(
            target="TARGET",
            table=TABLE_NAME,
        )
        assert ds.get_pod_identifiers() is None

    def test_get_pod_identifiers_with_multi_pod_datastructure(self) -> None:
        """Tests that `get_pod_identifiers` returns the correct identifiers."""
        ds = DataStructure(
            target="TARGET",
            table={"pod1": "pod1_table", "pod2": "pod2_table"},
        )
        assert ds.get_pod_identifiers() == ["pod1", "pod2"]

    def test_error_raised_for_incompatible_parameters(self) -> None:
        """Tests error is raised when incompatible parameters are given."""
        selected_cols = ["a", "b"]
        ignore_cols = ["c", "d"]
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                table=TABLE_NAME,
                selected_cols=selected_cols,
                ignore_cols=ignore_cols,
            )

    def test_both_table_and_query_error(self, query: str) -> None:
        """Tests error is raised when both table and query are given."""
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query=query,
                table=TABLE_NAME,
            )

    def test_both_query_no_schema_override_error(self, query: str) -> None:
        """Tests error is raised when query is given with no schema override."""
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query=query,
            )

    def test_both_query_selected_cols_error(self, query: str) -> None:
        """Tests error is raised when both selected_cols and query are given."""
        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
            "continuous": ["col2"],
        }
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query=query,
                schema_types_override=schema_override,
                selected_cols=["a"],
            )

    def test_both_query_ignore_cols_error(self, query: str) -> None:
        """Tests error is raised when both ignore_cols and query are given."""
        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
            "continuous": ["col2"],
        }
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query=query,
                schema_types_override=schema_override,
                ignore_cols=["a"],
            )

    def test_schema_overide_local_categorical_no_encodings_error(
        self, query: str
    ) -> None:
        """Tests error raised if schema override has categorical attr but no encoding.

        Test for datastructure meant for local training.
        """
        schema_override: SchemaOverrideMapping = {
            "categorical": ["col1"],
            "continuous": ["col2"],
        }
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query=query,
                schema_types_override=schema_override,
            )

    def test_schema_overide_remote_categorical_no_encodings_error(
        self, query: str
    ) -> None:
        """Tests error raised if schema override has categorical attr but no encoding.

        Test for datastructure meant for remote training.
        """
        schema_override: Dict[str, SchemaOverrideMapping] = {
            "pod_id": {
                "categorical": ["col1"],
                "continuous": ["col2"],
            },
        }
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query=query,
                schema_types_override=schema_override,
                ignore_cols=["a"],
            )

    def test_datastructure_no_query_no_table_error(self) -> None:
        """Tests error is raised with both query and table."""
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
            )

    def test_get_pod_identifiers_with_query_local_datastructure(
        self, query: str
    ) -> None:
        """Tests that `get_pod_identifiers` returns None if there are no pods."""
        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
            "continuous": ["col2"],
        }
        ds = DataStructure(
            target="TARGET", query=query, schema_types_override=schema_override
        )
        assert ds.get_pod_identifiers() is None

    def test_get_pod_identifiers_with_multi_pod_query(self, query: str) -> None:
        """Tests that `get_pod_identifiers` returns the correct identifiers."""
        schema_override: Dict[str, SchemaOverrideMapping] = {
            "pod1": {
                "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
                "continuous": ["col2"],
            },
            "pod2": {
                "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
                "continuous": ["col2"],
            },
        }
        ds = DataStructure(
            target="TARGET",
            query={"pod1": query, "pod2": query},
            schema_types_override=schema_override,
        )
        assert ds.get_pod_identifiers() == ["pod1", "pod2"]

    def test_query_pod_id_not_in_override(self, query: str) -> None:
        """Tests that pod_id not found in override raises error."""
        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
            "continuous": ["col2"],
        }
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query={"pod1": query, "pod2": query},
                schema_types_override=schema_override,
            )

    def test_query_pod_id_no_encodings(self, query: str) -> None:
        """Tests that pod_id not found in override raises error."""
        schema_override: Dict[str, SchemaOverrideMapping] = {
            "pod1": {
                "categorical": ["col1"],
                "continuous": ["col2"],
            },
            "pod2": {
                "categorical": ["col1"],
                "continuous": ["col2"],
            },
        }
        with pytest.raises(DataStructureError):
            DataStructure(
                target="TARGET",
                query={"pod1": query, "pod2": query},
                schema_types_override=schema_override,
            )

    def test_override_schema_raises_value_error(self) -> None:
        """Test that the schema overrides raises a ValueError if no query."""
        ds = DataStructure(target="TARGET", table="table")
        with pytest.raises(
            ValueError,
            match="No query or dictionary of pod_identifiers to queries was given.",
        ):
            ds._override_schema()

    def test_override_schema_local(self, query: str) -> None:
        """Test that the schema overrides returns the expected features."""
        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
            "continuous": ["col2"],
            "text": ["col3"],
            "image": ["col4"],
        }
        ds = DataStructure(
            target="TARGET", query=query, schema_types_override=schema_override
        )
        schema = ds._override_schema()
        assert "col1" in schema.features["categorical"]
        assert schema.features["categorical"]["col1"].encoder.size == 2
        assert "col2" in schema.features["continuous"]
        assert "col3" in schema.features["text"]
        assert "col4" in schema.features["image"]

    def test_override_schema_pod_id(self, query: str) -> None:
        """Test that the schema overrides returns the expected features."""
        pod_id = "pod_id"
        schema_override: Dict[str, SchemaOverrideMapping] = {
            pod_id: {
                "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
                "continuous": ["col2"],
                "text": ["col3"],
                "image": ["col4"],
            }
        }
        ds = DataStructure(
            target="TARGET",
            query={pod_id: query},
            schema_types_override=schema_override,
        )
        schema = ds._override_schema(pod_identifier=pod_id)
        assert "col1" in schema.features["categorical"]
        assert schema.features["categorical"]["col1"].encoder.size == 2
        assert "col2" in schema.features["continuous"]
        assert "col3" in schema.features["text"]
        assert "col4" in schema.features["image"]

    def test_override_schema_datasource(self, query: str) -> None:
        """Test that the schema overrides returns the expected features."""
        pod_id = "pod_id"
        schema_override: Dict[str, SchemaOverrideMapping] = {
            pod_id: {
                "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
                "continuous": ["col2"],
                "text": ["col3"],
                "image": ["col4"],
            }
        }
        ds = DataStructure(
            target="TARGET",
            query={pod_id: query},
            schema_types_override=schema_override,
        )
        data = {
            "col1": ["value_1", "value_2", "value_2"],
            "col2": [0, 1, 2],
            "col3": ["str1", "str2", "str3"],
            "col4": ["img1", "img2", "img3"],
            "col5": [0.2, 3, 24],
        }
        datasource = DataFrameSource(pd.DataFrame(data=data))
        datasource.load_data()
        schema = ds._override_schema(datasource, pod_id)
        assert "col1" in schema.features["categorical"]
        assert schema.features["categorical"]["col1"].encoder.size == 2
        assert "col2" in schema.features["continuous"]
        assert "col3" in schema.features["text"]
        assert "col4" in schema.features["image"]
        assert "col5" not in schema.features

    def test_update_datastructure_with_hub_identifiers_query(self, query: str) -> None:
        """Tests that the pod identifiers get updated."""
        pod_id = "pod_id"
        schema_override: Dict[str, SchemaOverrideMapping] = {
            pod_id: {
                "categorical": [{"col1": {"value_1": 0, "value_2": 1}}],
                "continuous": ["col2"],
                "text": ["col3"],
                "image": ["col4"],
            }
        }
        ds = DataStructure(
            target="TARGET",
            query={pod_id: query},
            schema_types_override=schema_override,
        )
        updated_pod_id = "testing/pod_id"
        ds._update_datastructure_with_hub_identifiers([updated_pod_id])
        assert isinstance(ds.query, dict)
        assert updated_pod_id in ds.query.keys()
        assert isinstance(ds.schema_types_override, dict)
        assert updated_pod_id in ds.schema_types_override.keys()
