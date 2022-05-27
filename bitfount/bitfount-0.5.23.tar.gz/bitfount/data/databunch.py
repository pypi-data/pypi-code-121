"""Classes concerning databunches."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from bitfount.data.datafactory import _DataFactory, _get_default_data_factory
from bitfount.data.types import DataSplit, SemanticType
from bitfount.utils import _add_this_to_list

if TYPE_CHECKING:
    from bitfount.data.dataloaders import _BitfountDataLoader
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.datasources.base_source import _BaseSource
    from bitfount.data.datastructure import DataStructure
    from bitfount.data.schema import TableSchema

logger = logging.getLogger(__name__)


class _BitfountDataBunch:
    """Wrapper for train, validation and test dataloaders.

    Provides methods to access dataloaders for training and evaluation. This is strictly
    a model concept and is not necessary for algorithms that do not have models.

    Args:
        data_structure: A `DataStructure` object.
        schema: A `TableSchema` object.
        datasource: A `_BaseSource` object.
        data_factory: A `_DataFactory` instance for creating datasets and dataloaders.
            Defaults to None.
    """

    def __init__(
        self,
        data_structure: DataStructure,
        schema: TableSchema,
        datasource: _BaseSource,
        data_factory: Optional[_DataFactory] = None,
    ):
        self.data_structure = data_structure
        self.schema = schema
        self.datasource = datasource
        self.data_factory = (
            data_factory if data_factory is not None else _get_default_data_factory()
        )

        # Column attributes
        self.target = self.data_structure.target
        self.loss_weights_col = self.data_structure.loss_weights_col
        self.multihead_col = self.data_structure.multihead_col
        self.ignore_classes_col = self.data_structure.ignore_classes_col

        # Placeholders for generated datasets
        self.train_ds: _BaseBitfountDataset  # training data is not optional
        self.validation_ds: Optional[_BaseBitfountDataset] = None
        self.test_ds: Optional[_BaseBitfountDataset] = None

        self.data_structure.set_training_column_split_by_semantic_type(self.schema)
        self._disallow_text_features()

        # TODO: [BIT-1167] This probably needs to be removed once we have implemented
        # dataset transformations. Currently, this call does nothing.
        self.datasource = self.data_structure.apply_dataset_transformations(
            self.datasource
        )
        self._load_data()
        self._create_datasets()

    def _load_data(self) -> None:
        """Loads the data from the datasource and applies dataset transformations."""
        kwargs = {}
        if isinstance(self.data_structure.query, str):
            kwargs["sql_query"] = self.data_structure.query

        if isinstance(self.data_structure.table, str):
            kwargs["table_name"] = self.data_structure.table

        # In the federated setting, the data should already have been loaded by the
        # Worker. So this call is effectively just for the local setting. The call is
        # idempotent so it doesn't matter if the data is already loaded.
        self.datasource.load_data(**kwargs)

    def _disallow_text_features(self) -> None:
        """Removes columns with semantic type TEXT from the data structure."""
        disallowed_columns = []
        for col in self.data_structure.selected_cols:
            if col in self.schema.get_feature_names(SemanticType.TEXT):
                disallowed_columns.append(col)
                logger.warning(
                    f"DataStructure has selected the text column {col} "
                    f"which is not supported. Removing this from the selection."
                )
        self.data_structure.ignore_cols = _add_this_to_list(
            disallowed_columns, self.data_structure.ignore_cols
        )
        self.data_structure.selected_cols = [
            i for i in self.data_structure.selected_cols if i not in disallowed_columns
        ]

    def _data_to_dataset(
        self,
        data_split: DataSplit,
    ) -> _BaseBitfountDataset:
        """Converts pandas dataframe to relevant BitfountDataset."""
        return self.data_factory.create_dataset(
            datasource=self.datasource,
            data_splitter=self.data_structure.data_splitter,
            target=self.target,
            schema=self.schema,
            selected_cols_semantic_types=self.data_structure.selected_cols_w_types,
            selected_cols=self.data_structure.selected_cols,
            batch_transforms=self.data_structure.get_batch_transformations(),
            data_split=data_split,
            weights_col=self.loss_weights_col,
            multihead_col=self.multihead_col,
            ignore_classes_col=self.ignore_classes_col,
        )

    def _create_datasets(self) -> None:
        """Creates datasets for dataloaders.

        Sets `self.train_ds`, `self.validation_ds` and `self.test_ds`
        """
        self.train_ds = self._data_to_dataset(DataSplit.TRAIN)
        self.validation_ds = self._data_to_dataset(DataSplit.VALIDATION)
        self.test_ds = self._data_to_dataset(DataSplit.TEST)

    def get_train_dataloader(
        self, batch_size: Optional[int] = None
    ) -> _BitfountDataLoader:
        """Gets the relevant data loader for training data."""
        return self.data_factory.create_dataloader(self.train_ds, batch_size=batch_size)

    def get_validation_dataloader(
        self, batch_size: Optional[int] = None
    ) -> Optional[_BitfountDataLoader]:
        """Gets the relevant data loader for validation data."""
        if not self.validation_ds:
            logging.warning(
                "No validation data in the dataset. Validation DataLoader is 'None'."
            )
            return None

        return self.data_factory.create_dataloader(
            self.validation_ds, batch_size=batch_size
        )

    def get_test_dataloader(
        self, batch_size: Optional[int] = None
    ) -> Optional[_BitfountDataLoader]:
        """Gets the relevant data loader for test data."""
        if not self.test_ds:
            logging.warning("No test data in the dataset. Test DataLoader is 'None'.")
            return None

        return self.data_factory.create_dataloader(self.test_ds, batch_size=batch_size)
