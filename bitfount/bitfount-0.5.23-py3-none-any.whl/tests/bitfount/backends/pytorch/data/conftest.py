"""Fixtures for pytorch data tests."""

import pandas as pd
from pytest import fixture

from bitfount.backends.pytorch.data.datasets import (
    _PyTorchDataset,
    _PyTorchIterableDataset,
)
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit, SemanticType
from tests.utils.helper import TABLE_NAME, create_dataset


@fixture
def dataframe() -> pd.DataFrame:
    """Underlying dataframe for dataset."""
    return create_dataset(image=True)


@fixture
def tabular_dataset(dataframe: pd.DataFrame) -> _PyTorchDataset:
    """Basic PyTorch tabular dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe)
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
    return _PyTorchDataset(
        datasource=datasource,
        target=target,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        selected_cols=datastructure.selected_cols,
        data_split=DataSplit.TRAIN,
        schema=schema.get_table_schema(TABLE_NAME),
    )


@fixture
def iter_tabular_dataset(dataframe: pd.DataFrame) -> _PyTorchIterableDataset:
    """Iterable PyTorch tabular dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe)
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
    return _PyTorchIterableDataset(
        datasource=datasource,
        target=target,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        selected_cols=datastructure.selected_cols,
        data_split=DataSplit.TRAIN,
        schema=schema.get_table_schema(TABLE_NAME),
    )


@fixture
def image_dataset(dataframe: pd.DataFrame) -> _PyTorchDataset:
    """Basic PyTorch image dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe)
    schema = BitfountSchema()
    schema.add_datasource_tables(
        datasource,
        force_stypes={TABLE_NAME: {"image": ["image"]}},
        table_name=TABLE_NAME,
    )
    datasource.load_data()
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(
        target=target, selected_cols=["image", "TARGET"], table=TABLE_NAME
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _PyTorchDataset(
        datasource=datasource,
        target=target,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        selected_cols=datastructure.selected_cols,
        schema=schema.get_table_schema(TABLE_NAME),
        data_split=DataSplit.TRAIN,
    )


@fixture
def image_tab_dataset(dataframe: pd.DataFrame) -> _PyTorchDataset:
    """Basic PyTorchPredictionDataset dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(dataframe)
    schema = BitfountSchema()
    schema.add_datasource_tables(
        datasource,
        force_stypes={TABLE_NAME: {"image": ["image"]}},
        table_name=TABLE_NAME,
    )
    datasource.load_data()
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(target=target, table=TABLE_NAME)
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _PyTorchDataset(
        datasource=datasource,
        target=target,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        selected_cols=datastructure.selected_cols,
        schema=schema.get_table_schema(TABLE_NAME),
        data_split=DataSplit.TRAIN,
    )


@fixture
def multiimage_dataframe() -> pd.DataFrame:
    """Underlying dataframe for multi-image dataset."""
    return create_dataset(multiimage=True)


@fixture
def multiimage_dataset(multiimage_dataframe: pd.DataFrame) -> _PyTorchDataset:
    """Basic multi-image dataset for tests as fixture."""
    target = "TARGET"
    datasource = DataFrameSource(multiimage_dataframe)
    schema = BitfountSchema()
    schema.add_datasource_tables(
        datasource,
        force_stypes={TABLE_NAME: {"image": ["image1", "image2"]}},
        table_name=TABLE_NAME,
    )
    datasource.load_data()
    datasource.data = datasource.data.drop(
        columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
    )
    datastructure = DataStructure(
        target=target, selected_cols=["image1", "image2", target], table=TABLE_NAME
    )
    datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
    return _PyTorchDataset(
        datasource=datasource,
        target=target,
        selected_cols_semantic_types=datastructure.selected_cols_w_types,
        selected_cols=datastructure.selected_cols,
        schema=schema.get_table_schema(TABLE_NAME),
        data_split=DataSplit.TRAIN,
    )
