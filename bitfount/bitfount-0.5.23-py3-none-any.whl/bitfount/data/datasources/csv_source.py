"""Module containing CSVSource class.

CSVSource class handles loading of CSV data.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd
from pydantic import AnyUrl

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.types import _Dtypes

logger = logging.getLogger(__name__)


class CSVSource(_BaseSource):
    """Data source for loading csv files.

    Args:
        path: The path to the csv file.
        **read_csv_kwargs: Additional arguments to be passed to `pandas.read_csv`.
    """

    def __init__(
        self,
        path: Union[os.PathLike, AnyUrl, str],
        read_csv_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        if not str(path).endswith(".csv"):
            raise TypeError("Please provide a Path or URL to a CSV file.")
        self.path = str(path)
        if not read_csv_kwargs:
            read_csv_kwargs = {}
        self.read_csv_kwargs = read_csv_kwargs

    def get_data(self, **kwargs: Any) -> pd.DataFrame:
        """Loads and returns data from CSV dataset.

        Returns:
            A DataFrame-type object which contains the data.
        """
        csv_df: pd.DataFrame = pd.read_csv(self.path, **self.read_csv_kwargs)
        return csv_df

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in CSV dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.

        """
        return {col: self.get_data()[col].unique() for col in col_names}

    def get_column(self, col_name: str, **kwargs: Any) -> Union[np.ndarray, pd.Series]:
        """Loads and returns single column from CSV dataset.

        Args:
            col_name: The name of the column which should be loaded.

        Returns:
            The column request as a series.
        """
        csv_df: pd.DataFrame = self.get_data()
        return csv_df[col_name]

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types of the CSV dataset.

        Returns:
            A mapping from column names to column types.
        """
        csv_df: pd.DataFrame = self.get_data()
        data = csv_df.convert_dtypes()
        dtypes: _Dtypes = data.dtypes.to_dict()
        return dtypes

    def __len__(self) -> int:
        return len(self.get_data())

    @property
    def multi_table(self) -> bool:
        """Attribute to specify whether the datasource is multi table."""
        return False
