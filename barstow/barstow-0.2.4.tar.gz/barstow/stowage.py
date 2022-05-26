from typing import Dict, List, Optional, Union
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.fs as fs

from .partitioning import Partitioning
from .dataset import Dataset


class Stowage:
    def __init__(
        self,
        location: str,
        schemas: Optional[Dict[str, pa.Schema]] = None,
        partitioning: Optional[Union[Partitioning, str]] = None,
        format="parquet",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
    ):
        if schemas is None:
            self._schemas = {}
        else:
            self._schemas = schemas
        self._format = format
        self._fs: fs.FileSystem = fs.LocalFileSystem()
        self._datasets: Dict[str, Dataset] = {}

        if isinstance(partitioning, str):
            self._partitioning = Partitioning(partitioning)
        elif partitioning is None:
            self._partitioning = Partitioning()
        else:
            self._partitioning = partitioning

        path = location
        if location.startswith("s3://"):
            self._fs = fs.S3FileSystem(
                access_key=access_key,
                secret_key=secret_key,
                region=region,
            )
            path = location[5:]
        self._path = Path(path)

    @property
    def schema(self):
        return self._schemas

    @property
    def format(self):
        return self._format

    def list_contents(self):
        files: List[fs.FileInfo] = self._fs.get_file_info(
            fs.FileSelector(str(self._path))
        )
        for file in files:
            print(file.path.split("/")[-1])

    def update_schemas(self, schema: Dict[str, pa.Schema]):
        self._schemas.update(schema)

    def load_dataset(self, name: str) -> Dataset:
        """Load a dataset from the filesystem"""
        dataset = self._datasets[name] = Dataset(
            str(self._path / name),
            format=self._format,
            filesystem=self._fs,
            partitioning=self._partitioning[name],
        )
        self._schemas[name] = dataset.schema
        return self._datasets[name]

    def create_from_dict(self, name: str, data: Dict[str, List]) -> ds.Dataset:
        """Create a dataset from a dictionary"""
        if name not in self._schemas:
            raise ValueError(f"Dataset {name} not found in schema")

        schema = self._schemas[name]

        # If a column exists in the schema, but it's not in the data, fill it with Nones
        data_length = len(data[[each for each in data][0]])
        for field in schema.names:
            if field not in data:
                data[field] = [None] * data_length

        table = pa.Table.from_pydict(data, schema=schema)
        dataset = self._datasets[name] = Dataset.from_pyarrow(
            ds.dataset([table]),
            filesystem=self._fs,
            format=self._format,
            partitioning=self._partitioning[name],
        )

        return dataset

    def to_pandas(
        self,
        name: str,
        columns: Optional[List[str]] = None,
        filter: Optional[ds.Expression] = None,
    ) -> pd.DataFrame:
        """Convert a dataset to a pandas DataFrame. Please note that the resulting DataFrame
        might not fit in memory. Request columns or filter the dataset to reduce the size."""
        if name not in self._datasets:
            dataset = self.load_dataset(name)
        else:
            dataset = self._datasets[name]

        if columns is None:
            return dataset.query.where(filter).to_pandas()
        else:
            return dataset.query.select(columns).where(filter).to_pandas()

    def save_dataset(self, name: str, mode="append"):
        """Saves dataset to location, appends if data is already there"""
        if name not in self._datasets:
            raise ValueError(f"Dataset {name} not found")

        # In-memory dataset
        dataset = self._datasets[name]
        dataset.write(location=str(self._path / name), mode=mode)

    def __getitem__(self, name: str) -> Dataset:
        if name not in self._datasets:
            raise ValueError(f"Dataset {name} not found")
        return self._datasets[name]

    def __delitem__(self, name: str):
        del self._datasets[name]
