"""Pytest fixtures for data tests."""

import pandas as pd
from pytest import fixture
import sqlalchemy

from bitfount.data.datasets import _BitfountDataset, _IterableBitfountDataset
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit, SemanticType
from bitfount.data.utils import DatabaseConnection
from tests.utils.helper import TABLE_NAME, create_dataset


@fixture
def dataframe() -> pd.DataFrame:
    """Underlying dataframe for single image datasets."""
    return create_dataset(image=True)


@fixture
def tabular_dataset(dataframe: pd.DataFrame) -> _BitfountDataset:
    """Basic tabular dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe, ignore_cols=["image"])
    datasource.load_data()

    schema = BitfountSchema()
    schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(
        target=target, ignore_cols=["image"], table=TABLE_NAME
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _BitfountDataset(
        datasource=datasource,
        target=target,
        selected_cols=datastructure.selected_cols,
        data_split=DataSplit.TRAIN,
        schema=schema.get_table_schema(TABLE_NAME),
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
    )


@fixture
def db_dataset(db_session: sqlalchemy.engine.base.Engine) -> _BitfountDataset:
    """Basic tabular dataset for tests as fixture."""
    target = "TARGET"
    db_conn = DatabaseConnection(db_session, table_names=["dummy_data", "dummy_data_2"])
    datasource = DatabaseSource(db_conn, seed=420)
    datasource.load_data(sql_query="SELECT * FROM dummy_data")

    schema = BitfountSchema()
    schema.add_datasource_tables(datasource, table_name="dummy_data")
    schema.add_datasource_tables(datasource, table_name="dummy_data_2")

    datastructure = DataStructure(
        target=target, ignore_cols=["image"], table="dummy_data"
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _BitfountDataset(
        datasource=datasource,
        target=target,
        selected_cols=datastructure.selected_cols,
        data_split=DataSplit.TRAIN,
        schema=schema.get_table_schema("dummy_data"),
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
    )


@fixture
def iter_tabular_dataset(dataframe: pd.DataFrame) -> _IterableBitfountDataset:
    """Basic tabular dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe, ignore_cols=["image"])
    datasource.load_data()

    schema = BitfountSchema()
    schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(
        target=target, ignore_cols=["image"], table=TABLE_NAME
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _IterableBitfountDataset(
        datasource=datasource,
        target=target,
        selected_cols=datastructure.selected_cols,
        data_split=DataSplit.TRAIN,
        schema=schema.get_table_schema(TABLE_NAME),
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
    )


@fixture
def iter_db_dataset(
    db_session: sqlalchemy.engine.base.Engine,
) -> _IterableBitfountDataset:
    """Basic tabular dataset for tests as fixture."""
    target = "TARGET"
    db_conn = DatabaseConnection(db_session, table_names=["dummy_data", "dummy_data_2"])
    datasource = DatabaseSource(db_conn, seed=420)
    datasource.load_data()

    schema = BitfountSchema()
    schema.add_datasource_tables(datasource, table_name="dummy_data")
    schema.add_datasource_tables(datasource, table_name="dummy_data_2")

    datastructure = DataStructure(
        target=target, ignore_cols=["image"], table="dummy_data"
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _IterableBitfountDataset(
        datasource=datasource,
        target=target,
        selected_cols=datastructure.selected_cols,
        data_split=DataSplit.TRAIN,
        schema=schema.get_table_schema("dummy_data"),
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
    )


@fixture
def image_dataset(dataframe: pd.DataFrame) -> _BitfountDataset:
    """Basic image dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe)
    datasource.load_data()
    schema = BitfountSchema(
        datasource,
        force_stypes={TABLE_NAME: {"image": ["image"]}},
        table_name=TABLE_NAME,
    )

    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(
        target=target,
        table=TABLE_NAME,
        selected_cols=["image", target],
        image_cols=["image"],
        batch_transforms=[
            {
                "image": {
                    "step": "train",
                    "output": True,
                    "arg": "image",
                    "transformations": [
                        {"Resize": {"height": 224, "width": 224}},
                        "Normalize",
                    ],
                }
            }
        ],
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _BitfountDataset(
        datasource=datasource,
        target=target,
        schema=schema.get_table_schema(TABLE_NAME),
        selected_cols=datastructure.selected_cols,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        batch_transforms=datastructure.get_batch_transformations(),
        data_split=DataSplit.TRAIN,
    )


@fixture
def image_tab_dataset(dataframe: pd.DataFrame) -> _BitfountDataset:
    """Basic tabular and image dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe)
    datasource.load_data()
    schema = BitfountSchema()
    schema.add_datasource_tables(
        datasource,
        force_stypes={TABLE_NAME: {"image": ["image"]}},
        table_name=TABLE_NAME,
    )
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(target=target, image_cols=["image"], table=TABLE_NAME)
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _BitfountDataset(
        datasource=datasource,
        target=target,
        selected_cols=datastructure.selected_cols,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        schema=schema.get_table_schema(TABLE_NAME),
        data_split=DataSplit.TRAIN,
    )


@fixture
def multiimage_dataframe() -> pd.DataFrame:
    """Underlying dataframe for multi-image dataset."""
    return create_dataset(multiimage=True)


@fixture
def multiimage_dataset(multiimage_dataframe: pd.DataFrame) -> _BitfountDataset:
    """Basic multi-image dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(multiimage_dataframe)
    datasource.load_data()
    schema = BitfountSchema()
    schema.add_datasource_tables(
        datasource,
        force_stypes={TABLE_NAME: {"image": ["image1", "image2"]}},
        table_name=TABLE_NAME,
    )
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(
        target=target,
        selected_cols=["image1", "image2", target],
        table=TABLE_NAME,
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])

    return _BitfountDataset(
        datasource=datasource,
        target=target,
        selected_cols=datastructure.selected_cols,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        schema=schema.get_table_schema(TABLE_NAME),
        data_split=DataSplit.TRAIN,
    )
