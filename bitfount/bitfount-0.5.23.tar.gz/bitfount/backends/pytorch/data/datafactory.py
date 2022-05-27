"""PyTorch implementations of the datafactory module contents."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union

from bitfount.backends.pytorch.data.dataloaders import (
    _BasePyTorchBitfountDataLoader,
    _PyTorchBitfountDataLoader,
    _PyTorchIterableBitfountDataLoader,
)
from bitfount.backends.pytorch.data.datasets import (
    _PyTorchDataset,
    _PyTorchIterableDataset,
)
from bitfount.data.datafactory import _DataFactory
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource

if TYPE_CHECKING:
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.datasplitters import DatasetSplitter
    from bitfount.data.schema import TableSchema
    from bitfount.data.types import DataSplit, _SemanticTypeValue
    from bitfount.transformations.batch_operations import BatchTimeOperation


class _PyTorchDataFactory(_DataFactory):
    """A PyTorch-specific implementation of the DataFactory provider."""

    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
    ) -> _BasePyTorchBitfountDataLoader:
        """See base class."""
        if isinstance(dataset, _PyTorchIterableDataset):
            return _PyTorchIterableBitfountDataLoader(
                dataset=dataset, batch_size=batch_size
            )
        elif isinstance(dataset, _PyTorchDataset):
            return _PyTorchBitfountDataLoader(dataset, batch_size=batch_size)

        raise TypeError(
            "The _PyTorchDataFactory class only supports "
            "subclasses of PyTorch Dataset for creating a DataLoader."
        )

    def create_dataset(
        self,
        datasource: _BaseSource,
        data_splitter: Optional[DatasetSplitter],
        data_split: DataSplit,
        schema: TableSchema,
        selected_cols: List[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, List[str]],
        target: Optional[Union[str, List[str]]] = None,
        batch_transforms: Optional[List[BatchTimeOperation]] = None,
        **kwargs: Any,
    ) -> Union[_PyTorchDataset, _PyTorchIterableDataset]:
        """See base class."""
        if datasource.multi_table and isinstance(datasource, DatabaseSource):
            return _PyTorchIterableDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=datasource,
                target=target,
                selected_cols=selected_cols,
                batch_transforms=batch_transforms,
                data_split=data_split,
                **kwargs,
            )

        return _PyTorchDataset(
            schema=schema,
            selected_cols_semantic_types=selected_cols_semantic_types,
            data_splitter=data_splitter,
            datasource=datasource,
            target=target,
            selected_cols=selected_cols,
            batch_transforms=batch_transforms,
            data_split=data_split,
            **kwargs,
        )
