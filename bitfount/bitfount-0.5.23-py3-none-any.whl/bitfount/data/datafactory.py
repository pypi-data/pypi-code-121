"""Data factory classes.

Factory design patterns for producing datasets and dataloaders.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union

from bitfount.config import _BASIC_ENGINE, _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.dataloaders import _BitfountDataLoader
from bitfount.data.datasets import _BaseBitfountDataset, _BitfountDataset
from bitfount.exceptions import BitfountEngineError

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import _BaseSource
    from bitfount.data.datasplitters import DatasetSplitter
    from bitfount.data.schema import TableSchema
    from bitfount.data.types import DataSplit, _SemanticTypeValue
    from bitfount.transformations.batch_operations import BatchTimeOperation


class _DataFactory(ABC):
    """A factory for producing dataset and dataloader instances."""

    def __init__(self, *args: Any, **kwargs: Any):
        pass

    @abstractmethod
    def create_dataloader(
        self, dataset: _BaseBitfountDataset, batch_size: Optional[int] = None
    ) -> _BitfountDataLoader:
        """Creates a dataloader as specified by this factory.

        Args:
            dataset: The dataset that should be loaded.
            batch_size: The batch size that the dataloader should output.

        Returns:
            A BitfountDataLoader instance.
        """
        raise NotImplementedError

    @abstractmethod
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
    ) -> _BaseBitfountDataset:
        """Creates a dataset for prediction tasks.

        Args:
            datasource: The data to wrap in a dataset.
            data_splitter: The data splitter to use, as specified by the Modeller.
            data_split: Which data split of the datasource to use and the step for which
                batch transformations should be applied.
            schema: The schema of the datasource.
            selected_cols: The columns selected by the data structure.
            selected_cols_semantic_types: A mapping of semantic types and column names.
            target: The dependent variable name.
            batch_transforms: A list of transformations to be applied at batch time.
            **kwargs: Any
        """
        raise NotImplementedError


class _BasicDataFactory(_DataFactory):
    """A basic DataFactory implementation using core dataset and dataloaders."""

    def create_dataloader(
        self, dataset: _BaseBitfountDataset, batch_size: Optional[int] = None
    ) -> _BitfountDataLoader:
        """See base class."""
        return _BitfountDataLoader(dataset, batch_size)

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
    ) -> _BaseBitfountDataset:
        """See base class."""
        return _BitfountDataset(
            datasource=datasource,
            schema=schema,
            data_splitter=data_splitter,
            data_split=data_split,
            target=target,
            selected_cols=selected_cols,
            selected_cols_semantic_types=selected_cols_semantic_types,
            batch_transforms=batch_transforms,
            **kwargs,
        )


def _get_default_data_factory(*args: Any, **kwargs: Any) -> _DataFactory:
    """Create a DataFactory instance as specified by the backend engine.

    Args:
        *args: positional arguments, passed to the DataFactory constructor.
        **kwargs: keyword arguments, passed to the DataFactory constructor.

    Returns:
        The created DataFactory instance.

    Raises:
        BitfountEngineError: if there is an import issue in loading the backend.
    """
    if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
        try:
            from bitfount.backends.pytorch.data.datafactory import _PyTorchDataFactory

            return _PyTorchDataFactory(*args, **kwargs)
        except ImportError:
            raise BitfountEngineError(
                "An error was encountered trying to load the pytorch engine; "
                "check pytorch is installed."
            )
    elif BITFOUNT_ENGINE == _BASIC_ENGINE:
        return _BasicDataFactory(*args, **kwargs)
    else:
        raise BitfountEngineError(f"Unable to load engine {BITFOUNT_ENGINE}.")
