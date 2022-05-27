"""Module containing DataFrameSource class.

DataFrameSource class handles loading data stored in memory in a pandas dataframe.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Union

import numpy as np
import pandas as pd

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.types import _Dtypes

logger = logging.getLogger(__name__)


class DataFrameSource(_BaseSource):
    """Data source for loading dataframes.

    Args:
        data: The dataframe to be loaded.
    """

    def __init__(self, data: pd.DataFrame, **kwargs: Any):
        if isinstance(data, pd.DataFrame):
            self.dataframe: pd.DataFrame = data
        else:
            raise TypeError(
                "Invalid data attribute. "
                "Expected pandas dataframe "
                f"but received :{type(data)}"
            )

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in DataFrame dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.
        """
        return {col: self.dataframe[col].unique() for col in col_names}

    def get_column(self, col_name: str, **kwargs: Any) -> Union[np.ndarray, pd.Series]:
        """Loads and returns single column from dataframe dataset.

        Args:
            col_name: The name of the column which should be loaded.

        Returns:
            The column request as a series.
        """
        return self.dataframe[col_name]

    def get_data(self, **kwargs: Any) -> pd.DataFrame:
        """Loads and returns datafrom DataFrame dataset.

        Returns:
            A DataFrame-type object which contains the data.
        """
        return self.dataframe

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types from the Dataframe dataset.

        Returns:
            A mapping from column names to column types.
        """
        data = self.dataframe.convert_dtypes()
        dtypes: _Dtypes = data.dtypes.to_dict()
        return dtypes

    def __len__(self) -> int:
        return len(self.dataframe)

    @property
    def multi_table(self) -> bool:
        """Attribute to specify whether the datasource is multi table."""
        return False
