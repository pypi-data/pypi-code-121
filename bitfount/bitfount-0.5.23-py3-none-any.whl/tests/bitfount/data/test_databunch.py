"""Tests databunch.py."""

import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.data.databunch import _BitfountDataBunch
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import SchemaOverrideMapping
from tests.utils import PytestRequest
from tests.utils.helper import (
    TABLE_NAME,
    create_dataset,
    create_datasource,
    create_schema,
    unit_test,
)


@unit_test
class TestBitfountDataBunch:
    """Tests for BitfountDataBunch class."""

    # TODO: [BIT-1098] Unskip this test once different schemas are suppported
    @pytest.mark.skip(
        reason="This is testing a state that is not supported yet. "
        "i.e. the schema should not have columns that are missing in the data."
    )
    def test_create_datasets_with_missing_columns(self) -> None:
        """Test that columns are created if they exist in schema.

        This tests whether a _BaseSource which is missing columns listed in the Schema
        has those missing columns added to it, to ensure that transformations
        can be applied across pods with varying schemas
        """
        dataset_with_all_columns = create_dataset()
        datasource_with_all_columns = DataFrameSource(dataset_with_all_columns)
        datasource_with_all_columns.load_data()
        schema_with_all_columns = BitfountSchema(
            datasource_with_all_columns,
            force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
            table_name=TABLE_NAME,
        )
        dataset_missing_some_columns = dataset_with_all_columns.drop(
            columns=["A", "B", "I"]
        )
        datasource = DataFrameSource(dataset_missing_some_columns)
        databunch = _BitfountDataBunch(
            data_structure=DataStructure(target="TARGET", table=TABLE_NAME),
            schema=schema_with_all_columns.tables[0],
            datasource=datasource,
        )

        assert databunch.validation_ds is not None
        assert databunch.test_ds is not None

        text_columns = ["I", "J", "K", "L"]
        assert set(databunch.train_ds.x_columns + databunch.train_ds.y_columns) == set(
            [i for i in dataset_with_all_columns.columns if i not in text_columns]
        )
        assert set(
            databunch.validation_ds.x_columns + databunch.validation_ds.y_columns
        ) == set([i for i in dataset_with_all_columns.columns if i not in text_columns])
        assert set(databunch.test_ds.x_columns + databunch.test_ds.y_columns) == set(
            [i for i in dataset_with_all_columns.columns if i not in text_columns]
        )


@unit_test
class TestCreateDataBunch:
    """Tests basic databunch generator."""

    @fixture(scope="function", params=[True, False])
    def datasource(self, request: PytestRequest) -> DataFrameSource:
        """Parameterised creation of DataFrameSource (with optional image col)."""
        data = create_dataset(image=request.param)
        if request.param:
            datasource = DataFrameSource(data, seed=420, image_col=["image"])
            datasource.load_data()
            return datasource

        datasource = DataFrameSource(data, seed=420)
        datasource.load_data()
        return datasource

    @fixture
    def datasource_w_loss_weights(self) -> _BaseSource:
        """Creates a datasource with loss_weights column."""
        ds = create_datasource(classification=True, loss_weights=True)
        ds.load_data()
        return ds

    @fixture
    def schema(self) -> BitfountSchema:
        """Creates a schema."""
        return create_schema(classification=True, loss_weights=True)

    def test_databunch_local_with_schema(self, datasource: _BaseSource) -> None:
        """Checks databunch creation with schema."""
        target = "TARGET"
        schema = BitfountSchema()
        schema.add_datasource_tables(
            datasource,
            force_stypes={TABLE_NAME: {"categorical": [target]}},
            table_name=TABLE_NAME,
        )
        datastructure = DataStructure(target=target, table=TABLE_NAME)

        db = _BitfountDataBunch(
            data_structure=datastructure, schema=schema.tables[0], datasource=datasource
        )
        assert target == db.target

    def test_datastructure_selected_and_ignore_cols_updated(
        self, datasource_w_loss_weights: _BaseSource, schema: BitfountSchema
    ) -> None:
        """Checks that the databunch updates the datstructure columns accordingly."""
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=[
                "E",
                "F",
                "G",
                "H",
                "M",
                "N",
                "O",
                "P",
                "TARGET",
                "weights",
            ],
            loss_weights_col="weights",
            table=TABLE_NAME,
        )
        db = _BitfountDataBunch(
            data_structure=datastructure,
            schema=schema.tables[0],
            datasource=datasource_w_loss_weights,
        )
        # Selected columns appear as specified in datastructure
        assert set(db.data_structure.selected_cols) == set(
            ["E", "F", "G", "H", "M", "N", "O", "P", "TARGET", "weights"]
        )
        # Any columns that are not part of the selected columns are ignored
        assert set(db.data_structure.ignore_cols) == set(
            ["A", "B", "C", "D", "I", "J", "K", "L", "Date"]
        )

    def test_databunch_text_columns_are_ignored_even_if_selected(
        self, datasource_w_loss_weights: _BaseSource, schema: BitfountSchema
    ) -> None:
        """Checks that the text columns are ignored even if selected."""
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=[
                "E",
                "F",
                "G",
                "H",
                "I",  # text
                "J",  # text
                "K",  # text
                "L",  # text
                "M",
                "N",
                "O",
                "P",
                "TARGET",
                "weights",
            ],
            loss_weights_col="weights",
            table=TABLE_NAME,
        )
        db = _BitfountDataBunch(
            data_structure=datastructure,
            schema=schema.tables[0],
            datasource=datasource_w_loss_weights,
        )
        assert set(db.data_structure.ignore_cols) == set(
            ["A", "B", "C", "D", "I", "J", "K", "L", "Date"]
        )

    def test_databunch_with_datastructure_query(
        self, datasource: DataFrameSource, mocker: MockerFixture
    ) -> None:
        """Test databunch calls load_data with sql_query arg."""
        mock_load_data = mocker.patch.object(_BaseSource, "load_data")
        mock_create_dataset = mocker.patch.object(
            _BitfountDataBunch, "_create_datasets"
        )

        target = "TARGET"
        schema = BitfountSchema()
        schema_override: SchemaOverrideMapping = {
            "categorical": [{"col1": {"value_1": 0, "value_2": 1}}]
        }
        schema.add_datasource_tables(
            datasource,
            force_stypes={TABLE_NAME: {"categorical": [target]}},
            table_name=TABLE_NAME,
        )
        datastructure = DataStructure(
            target=target,
            query="SELECT * from blah",
            schema_types_override=schema_override,
        )
        _BitfountDataBunch(
            data_structure=datastructure, schema=schema.tables[0], datasource=datasource
        )
        mock_load_data.assert_called_once_with(sql_query="SELECT * from blah")
        mock_create_dataset.assert_called_once()
