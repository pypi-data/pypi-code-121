"""Tests dataloaders.py."""
from typing import cast
from unittest.mock import MagicMock

import pytest
import sqlalchemy
import torch

from bitfount.backends.pytorch.data.dataloaders import (
    DEFAULT_BUFFER_SIZE,
    _PyTorchBitfountDataLoader,
    _PyTorchIterableBitfountDataLoader,
)
from bitfount.backends.pytorch.data.datasets import (
    _PyTorchDataset,
    _PyTorchIterableDataset,
)
from bitfount.data.databunch import _BitfountDataBunch
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.utils import DatabaseConnection
from tests.utils.helper import backend_test, integration_test, unit_test


@unit_test
@backend_test
class TestPyTorchBitfountDataLoader:
    """Tests _PyTorchBitfountDataLoader."""

    def test_iterator_tab_data(self, tabular_dataset: _PyTorchDataset) -> None:
        """Tests iteration of dataloader for tabular data."""
        batch_size = 16
        dl = _PyTorchBitfountDataLoader(dataset=tabular_dataset, batch_size=batch_size)
        dl_iterator = iter(dl)
        batch = next(dl_iterator)
        assert isinstance(batch, list)
        assert isinstance(batch[0], list)  # x data
        assert len(batch[0][0]) == batch_size  # tabular x data
        assert len(batch[0][1]) == batch_size  # x support columns
        assert len(batch[1]) == batch_size  # y data

    def test_iterator_image_data(self, image_dataset: _PyTorchDataset) -> None:
        """Tests iteration of dataloader for image data."""
        batch_size = 16
        dl = _PyTorchBitfountDataLoader(dataset=image_dataset, batch_size=batch_size)
        dl_iterator = iter(dl)
        batch = next(dl_iterator)
        assert isinstance(batch, list)
        assert isinstance(batch[0], list)  # x data
        assert len(batch[0][0]) == batch_size  # image x data
        assert len(batch[0][1]) == batch_size  # x support columns
        assert len(batch[1]) == batch_size  # y data

    def test_iterator_image_tab_data(self, image_tab_dataset: _PyTorchDataset) -> None:
        """Tests iteration of dataloader for mixed image and tabular data."""
        batch_size = 16
        dl = _PyTorchBitfountDataLoader(
            dataset=image_tab_dataset, batch_size=batch_size
        )
        dl_iterator = iter(dl)
        batch = next(dl_iterator)
        assert isinstance(batch, list)
        assert isinstance(batch[0], list)  # x data
        assert len(batch[0][0]) == batch_size  # tabular x data
        assert len(batch[0][1]) == batch_size  # image x data
        assert len(batch[0][2]) == batch_size  # x support columns
        assert len(batch[1]) == batch_size  # y data

    def test_dataloader_pytorch(self, image_tab_dataset: _PyTorchDataset) -> None:
        """Tests iteration of dataloader."""
        batch_size = 64
        dl = _PyTorchBitfountDataLoader(image_tab_dataset, batch_size=batch_size)
        iterator = iter(dl)
        output = next(iterator)
        assert isinstance(output, list)
        x, y = output
        assert len(x) == 3
        assert len(x[0]) == batch_size  # tabular
        assert len(x[1]) == batch_size  # image
        assert len(x[2]) == batch_size  # support
        assert len(y) == batch_size

    def test_dataloader_non_pytorch_img_tab(
        self, image_tab_dataset: _PyTorchDataset
    ) -> None:
        """Tests x- and y-dataframe retrieval from dataloader."""
        dl = _PyTorchBitfountDataLoader(image_tab_dataset)
        tab, img = dl.get_x_dataframe()
        y = dl.get_y_dataframe()
        assert len(tab) == len(y)
        assert len(img) == len(y)
        assert len(y.columns) == 1
        assert len(tab.columns) == 13
        assert len(img.columns) == 1


@backend_test
class TestPyTorchIterableBitfountDataLoader:
    """Tests _PyTorchIterableBitfountDataLoader."""

    @unit_test
    @pytest.mark.parametrize(
        "dataset_length,batch_size,expected_buffer_size",
        [
            # Dataset length is the expected buffer size since it is smaller than the
            # default buffer size.
            (100, 16, 100),
            # DEFAULT_BUFFER_SIZE is the expected buffer size since it is smaller than
            # the dataset length but larger than the batch size.
            (100000, 1, DEFAULT_BUFFER_SIZE),
            # Batch size is the expected buffer size since it is larger than the default
            # buffer size.
            (100, 1024, 1024),
        ],
    )
    def test_buffer_size(
        self, batch_size: int, dataset_length: int, expected_buffer_size: int
    ) -> None:
        """Tests buffer size property calculation."""
        dataset = MagicMock(spec=_PyTorchIterableDataset)
        dataset.__len__.return_value = dataset_length
        dataloader = _PyTorchIterableBitfountDataLoader(
            dataset=dataset, batch_size=batch_size
        )
        assert dataloader.buffer_size == expected_buffer_size

    @unit_test
    @pytest.mark.parametrize(
        "shuffle,secure_rng,batch_size,iterator_size",
        [
            # Tests with iterator that is smaller than the batch size
            (True, True, 8, 6),
            (False, False, 8, 7),
            # Tests with iterator that is equal to or just greater than the batch size
            (True, False, 8, 8),
            (False, False, 8, 9),
            # Tests with iterator that is significantly greater than the batch size
            # with no remainder
            (True, True, 32, 64),
            (False, False, 32, 96),
            # Tests with iterator that is significantly greater than the batch size
            # with a remainder
            (True, False, 32, 65),
            (False, False, 32, 325),
        ],
    )
    def test_iterator(
        self, batch_size: int, iterator_size: int, secure_rng: bool, shuffle: bool
    ) -> None:
        """Tests iteration of dataloader.

        The target of the batch (i.e. `batch[1]`) is used as a proxy for the rest of the
        batch for simplicity when it comes to checking shape and content.
        """
        dataset = MagicMock(spec=_PyTorchIterableDataset)
        dataset.__iter__.return_value = iter(
            [((i, i + 1), i + 2) for i in range(iterator_size)]
        )
        dataloader = _PyTorchIterableBitfountDataLoader(
            dataset=dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            secure_rng=secure_rng,
        )
        for i, batch in enumerate(dataloader, start=1):
            assert isinstance(batch, list)
            if iterator_size - (i * batch_size) >= batch_size:
                assert len(batch[1]) == batch_size
            else:  # last batch may have fewer elements
                assert len(batch[1]) <= batch_size

            if shuffle:
                # There is an extremely slim chance that the order of the elements in
                # the shuffled batch will be in the same order they started in but this
                # is negligible for our batch sizes as long as it is not the final batch
                # where there may be fewer elements (e.g. just 1).
                if len(batch[1]) == batch_size:
                    assert not torch.allclose(
                        torch.sort(cast(torch.Tensor, batch[1])).values,
                        cast(torch.Tensor, batch[1]),
                    )
            else:
                assert torch.allclose(
                    torch.sort(cast(torch.Tensor, batch[1])).values,
                    cast(torch.Tensor, batch[1]),
                )

    @integration_test
    @pytest.mark.parametrize("batch_size", [4, 128])
    def test_iterator_with_multi_table_database_connection(
        self, batch_size: int, db_session: sqlalchemy.engine.base.Engine
    ) -> None:
        """Tests iteration of dataloader with underlying database connection."""
        db_conn = DatabaseConnection(db_session)
        datasource = DatabaseSource(db_conn)
        schema = BitfountSchema(
            datasource,
            force_stypes={"dummy_data": {"categorical": ["TARGET"]}},
            table_name="dummy_data",
        )
        data_structure = DataStructure(target="TARGET", table="dummy_data")

        databunch = _BitfountDataBunch(
            data_structure=data_structure,
            schema=schema.get_table_schema("dummy_data"),
            datasource=datasource,
        )
        dataloader = databunch.get_train_dataloader(batch_size=batch_size)

        assert isinstance(dataloader, _PyTorchIterableBitfountDataLoader)
        assert len(next(iter(dataloader))[1]) == batch_size
