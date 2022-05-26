from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .query import Query
from .io import write_dataset


class Dataset:
    def __init__(
        self,
        location: Union[str, Path],
        partitioning: Optional[List[str]] = None,
        format: str = "parquet",
        filesystem: Optional[pa.fs.FileSystem] = None,
        batch_size: int = 1_000_000,
    ):
        self._location = location
        self._partitioning = partitioning
        self._format = format
        self._fs = filesystem
        self.batch_size = batch_size

        if self._location:
            self._dataset = ds.dataset(
                self._location,
                format=format,
                filesystem=filesystem,
                partitioning=partitioning,
            )

    @staticmethod
    def from_pyarrow(
        dataset: ds.Dataset,
        partitioning: Optional[List[str]] = None,
        format: str = "parquet",
        filesystem: Optional[pa.fs.FileSystem] = None,
    ) -> "Dataset":
        """Create a Dataset object from a local PyArrow dataset"""
        new_dataset = Dataset(
            location="",
            partitioning=partitioning,
            format=format,
            filesystem=filesystem,
        )

        new_dataset._dataset = dataset

        return new_dataset

    @property
    def location(self) -> Union[str, Path]:
        return self._location

    @property
    def schema(self) -> pa.Schema:
        return self._dataset.schema

    @property
    def nrows(self) -> int:
        nrows: int = self._dataset.count_rows()
        return nrows

    @property
    def dataset(self) -> ds.Dataset:
        return self._dataset

    @property
    def query(self) -> Query:
        """Returns a Query object that can be used to query the dataset"""
        return Query(self._dataset)

    def select(self, columns: List[str]):
        return self.query.select(columns)

    def where(self, expression: ds.Expression):
        return self.query.where(expression)

    def count_rows(self):
        return self.nrows

    def cast(self, **kwarg):
        """Cast a field in the dataset to another data type"""
        new_schema = self._dataset.schema

        for field, data_type in kwarg.items():
            idx = new_schema.get_field_index(field)
            new_schema = new_schema.set(idx, pa.field(field, data_type))

        if self._dataset.count_rows() > self.batch_size:
            # Dataset is too big to fit in memory, so we need to get it in batches and cast columns in each batch
            for batch in self._dataset.scanner(batch_size=self.batch_size).to_batches():
                table = pa.Table.from_batches([batch])
                new_table = table.cast(new_schema)

                dataset = ds.dataset(
                    [new_table],
                    schema=new_schema,
                )

                write_dataset(
                    dataset,
                    self.location,
                    new_schema,
                    format=self._format,
                    partitioning=self._partitioning,
                    filesystem=self._fs,
                    batch_size=self.batch_size,
                )
        else:
            table = self._dataset.to_table()
            new_table = table.cast(new_schema)

            dataset = ds.dataset([new_table], schema=new_schema)

            write_dataset(
                dataset,
                self.location,
                new_schema,
                format=self._format,
                partitioning=self._partitioning,
                filesystem=self._fs,
                batch_size=self.batch_size,
            )

    def write(self, location: Optional[Union[str, Path]] = None, mode="append"):
        """Save the dataset to a new location"""

        if location is None:
            if self._location == "":
                raise ValueError("Location to save to is not specified")
            else:
                location = self._location

        write_dataset(
            self._dataset,
            location,
            schema=self._dataset.schema,
            format=self._format,
            filesystem=self._fs,
            partitioning=self._partitioning,
            mode=mode,
        )

    def to_pandas(self) -> pd.DataFrame:
        """Returns the dataset as a Pandas DataFrame.

        Be aware that the dataset might be too large to fit in memory. Consider creating a query first."""
        return self._dataset.to_table().to_pandas()

    def __repr__(self):
        return f"Dataset(location={self._location})"
