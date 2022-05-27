"""Tests for PyTorchDataset classes."""
from typing import Union

from PIL import Image
import numpy as np
import pandas as pd
import pytest
import torch

from bitfount.backends.pytorch.data.datasets import _PyTorchDataset
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit, SemanticType
from tests.utils.helper import TABLE_NAME, backend_test, create_dataset, unit_test


@backend_test
@unit_test
class TestPyTorchDataset:
    """Tests for PyTorchTabularDataset class."""

    def test_len_tab_data(self, tabular_dataset: _PyTorchDataset) -> None:
        """Tests tabular dataset __len__ method."""
        assert tabular_dataset.datasource._train_idxs is not None
        assert len(tabular_dataset) == len(tabular_dataset.datasource._train_idxs)

    def test_len_image_data(self, image_dataset: _PyTorchDataset) -> None:
        """Tests image dataset __len__ method."""
        assert image_dataset.datasource._train_idxs is not None
        assert len(image_dataset) == len(image_dataset.datasource._train_idxs)

    def test_len_image_tab_data(self, image_tab_dataset: _PyTorchDataset) -> None:
        """Tests mixed dataset __len__ method."""
        assert image_tab_dataset.datasource._train_idxs is not None
        assert len(image_tab_dataset) == len(image_tab_dataset.datasource._train_idxs)

    def test_len_multiimage_data(self, multiimage_dataset: _PyTorchDataset) -> None:
        """Tests multi-image dataset __len__ method."""
        assert multiimage_dataset.datasource._train_idxs is not None
        assert len(multiimage_dataset) == len(multiimage_dataset.datasource._train_idxs)

    @pytest.mark.parametrize("idx", [0, 42, 2048, torch.tensor(3199)])
    def test_idx_tab_data(
        self, idx: Union[int, torch.Tensor], tabular_dataset: _PyTorchDataset
    ) -> None:
        """Tests indexing (incl. tensors) returns the expected formats of data."""
        assert isinstance(tabular_dataset[idx], tuple)
        assert len(tabular_dataset[idx]) == 2  # split into x,y
        assert len(tabular_dataset[idx][0]) == 2  # split into tabular, support
        assert len(tabular_dataset[idx][0][0]) == 13  # training cols  check
        assert len(tabular_dataset[idx][0][1]) == 2  # support cols check
        assert len([tabular_dataset[idx][1]]) == 1  # y check

    @pytest.mark.parametrize("idx", [0, 42, 2048, torch.tensor(3199)])
    def test_idx_img_data(self, idx: int, image_dataset: _PyTorchDataset) -> None:
        """Tests indexing returns the expected formats of data."""
        assert isinstance(image_dataset[idx], tuple)
        assert len(image_dataset[idx]) == 2  # split into x,y
        assert len(image_dataset[idx][0]) == 2  # split into image, support
        assert len(image_dataset[idx][0][1]) == 2  # support cols check
        assert len([image_dataset[idx][1]]) == 1  # y check

    @pytest.mark.parametrize("idx", [0, 42, 2048, torch.tensor(3199)])
    def test_idx_img_tab_data(
        self, idx: int, image_tab_dataset: _PyTorchDataset
    ) -> None:
        """Tests indexing returns the expected formats of data."""
        assert isinstance(image_tab_dataset[idx], tuple)
        assert len(image_tab_dataset[idx]) == 2  # split into x,y
        assert len(image_tab_dataset[idx][0]) == 3  # split into tab, image, support
        assert len(image_tab_dataset[idx][0][0]) == 13  # tabular cols  check
        # support cols check; mypy doesn't know that there are greater than 2 elements
        assert len(image_tab_dataset[idx][0][2]) == 2  # type: ignore[misc] # Reason: see above # noqa: B950
        assert len([image_tab_dataset[idx][1]]) == 1  # y check

    @pytest.mark.parametrize("idx", [0, 42, 2048, torch.tensor(3199)])
    def test_idx_multiimg_data(
        self, idx: int, multiimage_dataset: _PyTorchDataset
    ) -> None:
        """Tests indexing returns the expected formats of data."""
        assert isinstance(multiimage_dataset[idx], tuple)
        assert len(multiimage_dataset[idx]) == 2  # split into x,y
        assert len(multiimage_dataset[idx][0]) == 2  # split into image, support
        assert isinstance(multiimage_dataset[idx][0][0], tuple)
        assert len(multiimage_dataset[idx][0][0]) == 2  # image cols check
        assert len(multiimage_dataset[idx][0][1]) == 2  # support cols check
        assert len([multiimage_dataset[idx][1]]) == 1  # y check

    @pytest.mark.parametrize("idx", [0, 42, 2048, torch.tensor(3199)])
    def test_idx_img_tab_category(
        self, idx: int, image_tab_dataset: _PyTorchDataset
    ) -> None:
        """Tests indexing with categories gives expected data formats."""
        target = "TARGET"
        data = create_dataset(image=True, multihead=True)
        datasource = DataFrameSource(data, image_col=["image"])
        schema = BitfountSchema()
        schema.add_datasource_tables(
            datasource,
            force_stypes={
                TABLE_NAME: {"categorical": ["category"], "image": ["image"]}
            },
            table_name=TABLE_NAME,
        )
        datasource.load_data()
        datasource.data = datasource.data.drop(
            columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
        )
        datastructure = DataStructure(
            target=target, multihead_col="category", multihead_size=2, table=TABLE_NAME
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _PyTorchDataset(
            datasource=datasource,
            target=target,
            multihead_col="category",
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        assert isinstance(dataset[idx], tuple)
        assert len(dataset[idx]) == 2  # split into x,y
        assert len(dataset[idx][0]) == 3  # split into tab, image, support
        assert (
            len(dataset[idx][0][0]) == 14
        )  # tabular cols check (multihead_col included)
        # support cols check; mypy doesn't know that there are greater than 2 elements
        assert len(dataset[idx][0][2]) == 3  # type: ignore[misc] # Reason: see above # noqa: B950
        assert len([dataset[idx][1]]) == 1  # y check

    def test_dataset_works_only_with_continuous_features(
        self, dataframe: pd.DataFrame
    ) -> None:
        """Test no errors are raised if the dataset only has continuous features."""
        datasource = DataFrameSource(dataframe.loc[:, ["A", "B", "TARGET"]])
        datasource.load_data()
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datastructure = DataStructure(
            target=["TARGET"],
            table=TABLE_NAME,
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _PyTorchDataset(
            datasource=datasource,
            target=["TARGET"],
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        assert "categorical" not in schema.tables[0].features
        idx = 10
        assert isinstance(dataset[idx], tuple)
        assert len(dataset[idx]) == 2  # split into x,y
        assert len(dataset[idx][0]) == 2  # split into tabular, support
        assert len(dataset[idx][0][0]) == 2  # training cols  check
        assert len(dataset[idx][0][1]) == 2  # support cols check
        assert len([dataset[idx][1]]) == 1  # y check

    def test_dataset_works_without_target(self, dataframe: pd.DataFrame) -> None:
        """Test no errors are raised if the dataset has no target."""
        datasource = DataFrameSource(dataframe.loc[:, ["A", "B"]])
        datasource.load_data()
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datastructure = DataStructure(table=TABLE_NAME)
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _PyTorchDataset(
            datasource=datasource,
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        idx = 10
        assert isinstance(dataset[idx], tuple)
        assert len(dataset[idx]) == 2  # split into x,y
        assert len(dataset[idx][0]) == 2  # split into tabular, support
        assert len(dataset[idx][0][0]) == 2  # training cols  check
        assert len(dataset[idx][0][1]) == 2  # support cols check
        assert len([dataset[idx][1]]) == 1  # y check
        for i in range(0, len(dataset)):
            assert dataset[i][1] == 0  # all target values default to 0.

    def test_dataset_works_only_with_categorical_features(
        self, dataframe: pd.DataFrame
    ) -> None:
        """Test no errors are raised if the dataset only has categorical features."""
        datasource = DataFrameSource(dataframe.loc[:, ["M", "N", "TARGET"]])
        datasource.load_data()
        schema = BitfountSchema()
        schema.add_datasource_tables(
            datasource,
            force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
            table_name=TABLE_NAME,
        )
        datastructure = DataStructure(target=["TARGET"], table=TABLE_NAME)
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _PyTorchDataset(
            datasource=datasource,
            target=["TARGET"],
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            schema=schema.get_table_schema(TABLE_NAME),
            data_split=DataSplit.TRAIN,
        )
        assert "continuous" not in schema.tables[0].features
        idx = 10
        assert isinstance(dataset[idx], tuple)
        assert len(dataset[idx]) == 2  # split into x,y
        assert len(dataset[idx][0]) == 2  # split into tabular, support
        assert len(dataset[idx][0][0]) == 2  # training cols  check
        assert len(dataset[idx][0][1]) == 2  # support cols check
        assert len([dataset[idx][1]]) == 1  # y check

    def test_transform_image_with_default_batch_transformations(
        self, dataframe: pd.DataFrame
    ) -> None:
        """Test that the default transformations are applied to the image correctly.

        This is done for every split.
        """
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
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])

        # Iterate over all data splits
        for split in DataSplit:
            image_dataset = _PyTorchDataset(
                datasource=datasource,
                target=target,
                schema=schema.get_table_schema(TABLE_NAME),
                selected_cols=datastructure.selected_cols,
                selected_cols_semantic_types=datastructure.selected_cols_w_types,
                batch_transforms=datastructure.get_batch_transformations(),
                data_split=split,
            )

            # Make assertions
            assert image_dataset.batch_transforms is not None
            img_array = np.array(Image.new("RGB", size=(224, 224), color=(55, 100, 2)))
            transformed_image = image_dataset._transform_image(img_array.copy(), 0)
            assert isinstance(transformed_image, torch.Tensor)

            # Torch transformation resizes the image so that the channels are first
            assert transformed_image.shape == (3, 224, 224)
            torch_img_array = torch.from_numpy(img_array)
            assert torch_img_array.shape == (224, 224, 3)

            # Check that the image dtypes are different because the transformed image
            # has been normalized. The actual tensors cannot be compared with eachother
            # because the dtypes are different.
            assert torch_img_array.dtype != transformed_image.dtype
