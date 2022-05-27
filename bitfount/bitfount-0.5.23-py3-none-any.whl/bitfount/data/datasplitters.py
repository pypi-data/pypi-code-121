"""Classes for splitting data."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import random
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from bitfount.data.types import DataSplit

if TYPE_CHECKING:
    from bitfount.data.datasources.database_source import DatabaseSource


logger = logging.getLogger(__name__)


class DatasetSplitter(ABC):
    """Parent class for different types of dataset splits."""

    # TODO: [BIT-1053] If we're using python 3.9 we can stack property here too
    @classmethod
    @abstractmethod
    def splitter_name(cls) -> str:
        """Returns string name for splitter type."""
        raise NotImplementedError()

    @abstractmethod
    def create_dataset_splits(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns indices for data sets."""
        raise NotImplementedError

    @abstractmethod
    def get_split_query(self, datasource: DatabaseSource, split: DataSplit) -> str:
        """Modifies the loader SQL query to return a split of the data.

        Args:
            loader: A `DatabaseLoader` object.
            split: The relevant split to return from the query.

        Returns:
            The modified SQL query.
        """
        raise NotImplementedError

    @classmethod
    def create(cls, splitter_name: str, **kwargs: Any) -> DatasetSplitter:
        """Create a DataSplitter of the requested type."""
        # We may want to replace this with an `__init_subclass_` based
        # approach if we start adding more DataSplitters
        # See: https://blog.yuo.be/2018/08/16/__init_subclass__-a-simpler-way-to-implement-class-registries-in-python/ # noqa: B950
        if splitter_name == SplitterDefinedInData.splitter_name():
            return SplitterDefinedInData(**kwargs)
        return PercentageSplitter(**kwargs)


@dataclass
class PercentageSplitter(DatasetSplitter):
    """Splits data into sets based on percentages.

    The default split is 80% of the data is used training, and 10% for each
    validation and testing, respectively.

    Args:
        validation_percentage: The percentage of data to be used for validation.
            Defaults to 10.
        test_percentage: The percentage of data to be used for testing.
            Defaults to 10.
        time_series_sort_by: A string/list of strings to be used for sorting
            time series. The strings should correspond to feature names from the
            dataset. This sorts the dataframe by the values of those features
            ensuring the validation and test sets come after the training set data
            to remove potential bias during training and evaluation. Defaults to None.
    """

    validation_percentage: int = 10
    test_percentage: int = 10
    time_series_sort_by: Optional[Union[List[str], str]] = None

    def __post_init__(self) -> None:
        self.train_percentage = 100 - self.validation_percentage - self.test_percentage

    @classmethod
    def splitter_name(cls) -> str:
        """Class method for splitter name.

        Returns:
            The string name for splitter type.
        """
        return "percentage"

    def create_dataset_splits(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create splits in dataset for training, validation and test sets.

        Args:
            data: The dataframe type object to be split.

        Returns:
              A tuple of arrays, each containing the indices from the data
              to be used for training, validation, and testing, respectively.
        """
        # Sort or shuffle data depending on time_series constraint
        if self.time_series_sort_by:
            data = data.sort_values(by=self.time_series_sort_by)

        # Get indices of dataframe
        indices = data.index.to_series().to_list()

        if not self.time_series_sort_by:
            random.shuffle(indices)

        # Create dataset splits
        train_idxs, validation_idxs, test_idxs = np.split(
            indices,
            [
                int(
                    (100 - self.validation_percentage - self.test_percentage)
                    * len(indices)
                    / 100
                ),
                int((100 - self.test_percentage) * len(indices) / 100),
            ],
        )

        # Ensure that time series constraint is enforced correctly
        if self.time_series_sort_by:
            validation_idxs, test_idxs = self._split_indices_time_series(
                validation_idxs, test_idxs, data
            )
            train_idxs, validation_idxs = self._split_indices_time_series(
                train_idxs, validation_idxs, data
            )

            if self.validation_percentage == 0 and self.test_percentage != 0:
                train_idxs, test_idxs = self._split_indices_time_series(
                    train_idxs, test_idxs, data
                )

            np.random.shuffle(train_idxs)
            np.random.shuffle(validation_idxs)
            np.random.shuffle(test_idxs)

        return train_idxs, validation_idxs, test_idxs

    def get_split_query(self, datasource: DatabaseSource, split: DataSplit) -> str:
        """Modifies the loader SQL query to return a split of the data.

        Args:
            loader: A `DatabaseLoader` object.
            split: The relevant split to return from the query.

        Returns:
            The modified SQL query.

        :::caution

        This method will only work for databases that support the `LIMIT ... OFFSET`
        syntax. Notably, Microsoft SQL Server does not support this syntax.

        :::

        :::caution

        It is strongly recommended that you sort the data as part of the SQL query in
        order to ensure the splits are random. This is because for iterable datasets,
        the splits are simply taken in order from TRAIN to TEST.

        Similarly, `time_series_sort_by` is ignored and a warning logged if True. If you
        want to sort by time series, you should do this as part of the SQL Query.

        :::
        """
        if self.time_series_sort_by:
            logger.warning(
                "Time series sort by is not supported for Database percentage splits. "
                "The sort by will be ignored. If you want to use time series sort by, "
                "please sort the dataset as you want in the SQL query."
            )

        len_loader = len(datasource)

        if split == DataSplit.TRAIN:
            limit = int(len_loader * self.train_percentage / 100)
            offset = 0
        elif split == DataSplit.VALIDATION:
            limit = int(len_loader * self.validation_percentage / 100)
            offset = int(len_loader * self.train_percentage / 100)
        elif split == DataSplit.TEST:
            limit = int(len_loader * self.test_percentage / 100)
            offset = int(len_loader * (100 - self.test_percentage) / 100)
        else:
            raise ValueError("Split not recognised")

        # Ignoring the security warning because the sql query is trusted and
        # will be executed regardless.
        return f"SELECT * FROM ({datasource.query}) q LIMIT {limit} OFFSET {offset}"  # nosec # noqa: B950

    def _split_indices_time_series(
        self, index_array_a: np.ndarray, index_array_b: np.ndarray, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Splits indices in a chronological fashion.

        Helper function which ensures that two arrays of indices of the full
        dataset do not overlap in terms of dates to ensure there is no
        information leakage. This is necessary when there is not enough
        granularity in the dates provided yet we still want to make sure that
        e.g. all the samples in the test set definitely come after the
        validation set and so on. For example in the LendingClub data we are
        only given month and year - this function ensures that the
        training/validation/test splits only occur at month boundaries.
        Args:
            index_array_a: An array of indices from the full dataset.
            index_array_b: An array of indices from the full dataset.
            data: A dataframe type object.

        Returns:
             The two arrays of indices modified by moving items from
             index_list_a into index_list_b until the condition is satisfied.
        """
        # Get the most granular time series column
        time_series_col: Optional[str]
        if isinstance(self.time_series_sort_by, list):
            time_series_col = self.time_series_sort_by[-1]
        else:
            time_series_col = self.time_series_sort_by

        # Return if one of the arrays is empty
        if len(index_array_a) == 0 or len(index_array_b) == 0:
            return index_array_a, index_array_b

        first_val_b = data[time_series_col].loc[index_array_b[0].item()]
        last_val_a = data[time_series_col].loc[index_array_a[-1].item()]

        # Move data from a to b whilst condition is still satisfied
        while first_val_b == last_val_a:
            last_idx_a, index_array_a = index_array_a[-1], index_array_a[:-1]
            index_array_b = np.insert(index_array_b, 0, last_idx_a)

            if index_array_a.size == 0:
                raise ValueError(
                    "One or more of the training/test/validation sets ends "
                    "up empty in the _split_indices_time_series() function. "
                    "This is because one of the sets contains only one unique date."
                )
            first_val_b = data[time_series_col].loc[index_array_b[0].item()]
            last_val_a = data[time_series_col].loc[index_array_a[-1].item()]

        return index_array_a, index_array_b


@dataclass
class SplitterDefinedInData(DatasetSplitter):
    """Splits data into sets based on value in each row.

    The splitting is done based on the values in a user specified column.

    Args:
        column_name: The column name for which contains the labels
            for splitting. Defaults to "BITFOUNT_SPLIT_CATEGORY".
        training_set_label: The label for the data points to be included
            in the training set. Defaults to "TRAIN".
        validation_set_label: The label for the data points to be included
            in the validation set. Defaults to "VALIDATE".
        test_set_label: The label for the data points to be included in
            the test set. Defaults to "TEST".
    """

    column_name: str = "BITFOUNT_SPLIT_CATEGORY"
    training_set_label: str = "TRAIN"
    validation_set_label: str = "VALIDATE"
    test_set_label: str = "TEST"

    @classmethod
    def splitter_name(cls) -> str:
        """Class method for splitter name.

        Returns:
            The string name for splitter type.
        """
        return "predefined"

    def create_dataset_splits(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create splits in dataset for training, validation and test sets.

        Args:
            data: The dataframe type object to be split.

        Returns:
              A tuple of arrays, each containing the indices from the data
              to be used for training, validation, and testing, respectively.
        """
        training_indices = data[
            data[self.column_name] == self.training_set_label
        ].index.values
        validation_indices = data[
            data[self.column_name] == self.validation_set_label
        ].index.values
        test_indices = data[data[self.column_name] == self.test_set_label].index.values
        return training_indices, validation_indices, test_indices

    def get_split_query(self, datasource: DatabaseSource, split: DataSplit) -> str:
        """Modifies the loader SQL query to return a split of the data.

        Args:
            loader: A `DatabaseLoader` object.
            split: The relevant split to return from the query.

        Returns:
            The modified SQL query.
        """
        if split == DataSplit.TRAIN:
            # Ignoring the security warning because the sql query is trusted and
            # will be executed regardless.
            query = (
                f"SELECT * FROM ({datasource.query}) q "  # nosec # Reason: See above
                f"WHERE {self.column_name} = '{self.training_set_label}'"
            )
        elif split == DataSplit.VALIDATION:
            query = (
                f"SELECT * FROM ({datasource.query}) q "  # nosec # Reason: See above
                f"WHERE {self.column_name} = '{self.validation_set_label}'"
            )
        elif split == DataSplit.TEST:
            query = (
                f"SELECT * FROM ({datasource.query}) q "  # nosec # Reason: See above
                f"WHERE {self.column_name} = '{self.test_set_label}'"
            )
        else:
            raise ValueError("Split not recognised")

        return query
