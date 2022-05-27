"""Tests dataloaders.py."""
import numpy as np
import pandas as pd
import pytest
from pytest import fixture

from bitfount.data.dataloaders import _BitfountDataLoader
from bitfount.data.datasets import _BitfountDataset
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasplitters import PercentageSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit, SemanticType
from tests.utils.helper import TABLE_NAME, create_dataset, unit_test


class TestDataLoaders:
    """Tests BitfountDataloader."""

    @fixture
    def dataframe(self) -> pd.DataFrame:
        """Dataframe fixture."""
        df = create_dataset(image=True)
        # Drop the date column until we support datetime.
        return df.drop(columns=["Date"])

    @unit_test
    def test_get_x_dataframe_tabular_only(self, dataframe: pd.DataFrame) -> None:
        """Tests get_x_dataframe for tabular data."""
        df = dataframe.drop(columns=["image"])
        datasource = DataFrameSource(df)
        datasource.load_data()
        datastucture = DataStructure(target="TARGET", table=TABLE_NAME)
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datastucture.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=datasource,
            target="TARGET",
            selected_cols_semantic_types=datastucture.selected_cols_w_types,
            selected_cols=datastucture.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        dl = _BitfountDataLoader(dataset=dataset)
        x_df = dl.get_x_dataframe()
        # Drop target and text columns
        new_df = df.drop(columns=["TARGET", "I", "J", "K", "L"])
        assert isinstance(x_df, pd.DataFrame)
        assert set(x_df.columns) == set(new_df.columns)

    @unit_test
    def test_get_x_dataframe_image_only(self, dataframe: pd.DataFrame) -> None:
        """Tests get_x_dataframe for tabular data."""
        df = dataframe[["image", "TARGET"]]
        datasource = DataFrameSource(df, data_splitter=PercentageSplitter(0, 0))
        datasource.load_data()
        datastucture = DataStructure(
            target="TARGET", table=TABLE_NAME, selected_cols=["image", "TARGET"]
        )
        schema = BitfountSchema()
        schema.add_datasource_tables(
            datasource,
            force_stypes={TABLE_NAME: {"image": ["image"]}},
            table_name=TABLE_NAME,
        )
        datastucture.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=datasource,
            target="TARGET",
            selected_cols_semantic_types=datastucture.selected_cols_w_types,
            selected_cols=datastucture.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        dl = _BitfountDataLoader(dataset=dataset)
        x_df = dl.get_x_dataframe()
        assert isinstance(x_df, pd.DataFrame)
        assert x_df.shape == df[["image"]].shape
        assert x_df.columns == df[["image"]].columns

    @unit_test
    def test_get_x_dataframe_image_and_tab(self, dataframe: pd.DataFrame) -> None:
        """Tests get_x_dataframe for tabular data."""
        datasource = DataFrameSource(dataframe, data_splitter=PercentageSplitter(0, 0))
        datasource.load_data()
        datastucture = DataStructure(target="TARGET", table=TABLE_NAME)
        schema = BitfountSchema()
        schema.add_datasource_tables(
            datasource,
            force_stypes={TABLE_NAME: {"image": ["image"]}},
            table_name=TABLE_NAME,
        )
        datastucture.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=datasource,
            target="TARGET",
            selected_cols_semantic_types=datastucture.selected_cols_w_types,
            selected_cols=datastucture.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        dl = _BitfountDataLoader(dataset=dataset)
        x_df = dl.get_x_dataframe()
        # Drop target, image, and text columns
        new_df = dataframe.drop(columns=["TARGET", "I", "J", "K", "L", "image"])
        # x_df is a tuple of dataframes (tabular followed by image)
        assert isinstance(x_df, tuple)
        assert set(x_df[0].columns) == set(new_df.columns)
        assert isinstance(x_df[1], pd.DataFrame)
        assert x_df[1].shape == dataframe[["image"]].shape
        assert x_df[1].columns == dataframe[["image"]].columns

    @unit_test
    def test_empty_dataframe_raises_valerror(self, dataframe: pd.DataFrame) -> None:
        """Tests get_x_dataframe with empty df raises error."""
        df = pd.DataFrame(dataframe[["TARGET"]])
        datasource = DataFrameSource(df)
        datasource.load_data()
        datastucture = DataStructure(
            target="TARGET", selected_cols=["TARGET"], table=TABLE_NAME
        )
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datastucture.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=datasource,
            target="TARGET",
            selected_cols_semantic_types=datastucture.selected_cols_w_types,
            selected_cols=datastucture.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        dl = _BitfountDataLoader(dataset=dataset)
        with pytest.raises(ValueError):
            dl.get_x_dataframe()

    @unit_test
    def test_dataloader_tab(self, tabular_dataset: _BitfountDataset) -> None:
        """Tests x- and y-dataframe retrieval from dataloader for tabular data."""
        df = _BitfountDataLoader(tabular_dataset)
        x = df.get_x_dataframe()
        y = df.get_y_dataframe()
        assert isinstance(x, pd.DataFrame)
        assert len(x) == len(y)
        assert len(x.columns) == 12
        assert len(y.columns) == 1

    @unit_test
    def test_dataloader_img(self, image_dataset: _BitfountDataset) -> None:
        """Tests x- and y-dataframe retrieval from dataloader for image data."""
        df = _BitfountDataLoader(image_dataset)
        x = df.get_x_dataframe()
        y = df.get_y_dataframe()
        assert isinstance(x, pd.DataFrame)
        assert len(x) == len(y)
        assert len(x.columns) == 1
        assert len(y.columns) == 1

    @unit_test
    def test_dataloader_img_tab(self, image_tab_dataset: _BitfountDataset) -> None:
        """Tests x- and y-dataframe retrieval from dataloader."""
        df = _BitfountDataLoader(image_tab_dataset)
        x = df.get_x_dataframe()
        y = df.get_y_dataframe()
        assert isinstance(x, tuple)
        tab, img = x
        assert len(tab) == len(y)
        assert len(img) == len(y)
        assert len(y.columns) == 1
        assert len(tab.columns) == 12
        assert len(img.columns) == 1

    @unit_test
    def test_dataloader_multiimage(self, multiimage_dataset: _BitfountDataset) -> None:
        """Tests x- and y-dataframe retrieval from dataloader for multi-image."""
        df = _BitfountDataLoader(multiimage_dataset)
        x = df.get_x_dataframe()
        y = df.get_y_dataframe()
        assert isinstance(x, pd.DataFrame)
        assert len(x) == len(y)
        assert len(x.columns) == 2
        assert len(y.columns) == 1

    @unit_test
    def test_dataloader_multilabel(self) -> None:
        """Tests x- and y-dataframe retrieval from dataloader for multilabel target."""
        data = create_dataset(image=True)
        data = data.assign(TARGET_2=np.zeros(len(data)))
        data.loc[(data.A < 700) & (data.F < 0.5) & (data.D % 2 == 1), "TARGET_2"] = 1
        datasource = DataFrameSource(data)
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
        datastructure = DataStructure(target=["TARGET", "TARGET_2"], table=TABLE_NAME)
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        multilabel_dataset = _BitfountDataset(
            datasource=datasource,
            target=["TARGET", "TARGET_2"],
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        df = _BitfountDataLoader(multilabel_dataset)
        x = df.get_x_dataframe()
        y = df.get_y_dataframe()
        assert isinstance(x, tuple)
        tab, img = x
        assert len(tab) == len(y)
        assert len(img) == len(y)
        assert len(y.columns) == 2
        assert len(tab.columns) == 13
        assert len(img.columns) == 1
