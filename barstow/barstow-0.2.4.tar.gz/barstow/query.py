from typing import List, Generator, Optional

import pyarrow.dataset as ds
import pandas as pd


field = ds.field


class Query:
    def __init__(self, dataset: ds.Dataset):
        self._dataset = dataset
        self._columns: Optional[List[str]] = None
        self._filter = None

    def select(self, columns: List[str]) -> "Query":
        """Select specific columns from the dataset"""
        self._columns = columns
        return self

    def where(self, expression: ds.Expression) -> "Query":
        """Filter the dataset, returns the query object.

        Refer to PyArrow documentation for information on creating expressions:
          https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html
        """
        if self._filter is not None:
            self._filter = self._filter & expression
        else:
            self._filter = expression
        return self

    def count_rows(self) -> int:
        """Return the number of rows to be returned by the current query"""
        nrows: int = self._dataset.scanner(
            columns=self._columns, filter=self._filter
        ).count_rows()

        return nrows

    def to_pandas(self) -> pd.DataFrame:
        """Fetch the data from the dataset and return it as a Pandas DataFrame"""
        return (
            self._dataset.scanner(columns=self._columns, filter=self._filter)
            .to_table()
            .to_pandas()
        )

    def to_batches(self, batch_size=1_000_000) -> Generator[pd.DataFrame, None, None]:
        """Fetch the data from the dataset as batches and return a generator that yields each
        batch as a Pandas DataFrame"""
        for batch in self._dataset.scanner(
            columns=self._columns, filter=self._filter, batch_size=batch_size
        ).to_batches():
            yield batch.to_pandas()

    def __repr__(self):
        return "Query(columns={}, filter={})".format(self._columns, self._filter)
