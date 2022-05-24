import abc
import logging
import os
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Tuple

import pandas as pd

from .config import GOOGLE_PROJECT_ID


@dataclass(kw_only=True)
class Target(abc.ABC):
    """Base class for all targets."""

    target: str

    @abstractmethod
    def save(self, tbl):
        pass


@dataclass(kw_only=True)
class PartitionedFileTarget(Target):
    """Base class for targets that create partitioned files."""

    filetype: str
    partition_cols: list[str] = field(default_factory=list)

    @abstractmethod
    def construct_path(self, partition_path=None) -> str:
        pass

    def pre_save_object(self, path):
        pass

    def save(self, tbl):
        if self.partition_cols:
            partitions = tbl.df.groupby(self.partition_cols)
            for partition in partitions:

                if len(self.partition_cols) == 1:
                    # 1 partition col
                    partition_path = f"{self.partition_cols[0]}={partition[0]}"
                else:
                    # multiple partition cols
                    partition_path = '/'.join((f"{p}={v}" for p,v in zip(self.partition_cols, partition[0])))

                path = self.construct_path(partition_path)

                df = partition[1].drop(self.partition_cols, axis=1)
                self.save_object(df, path)

        else:
            path = self.construct_path()
            self.save_object(tbl.df, path)

    def save_object(self, df, path):

        self.pre_save_object(path)

        logging.debug(f"saving data to {path}")
        match self.filetype:
            case 'csv':
                df.to_csv(path, index=False)
            case 'parquet':
                df.to_parquet(path, index=False)
            case _:
                raise Exception(f"unrecognised filetype: [{self.filetype}]")


@dataclass(kw_only=True)
class CloudStorage(PartitionedFileTarget, Target):
    """
    Target that creates files in cloud storage.

    Supports csv and parquet `filetype`s.

    Usage:

        targets:
        - target: CloudStorage
          filetype: csv / parquet
          bucket: mybucket # the cloud storage bucket to save to
          prefix: my/prefix # the path prefix to give to all objects
          filename: myfile.csv # the name of the file

          # Optional params
          partition_cols: [col1, col2] # Optional. The columns within the dataset to partition on.


    If partition_cols is specified then data will be split into separate files and loaded to cloud storage
    with filepaths that follow the hive partitioning structure.
    e.g. If a dataset has dt and currency columns and these are specified as partition_cols
    then you might expect the following files to be created:
    - gs://bucket/prefix/dt=2022-01-01/currency=USD/filename
    - gs://bucket/prefix/dt=2022-01-01/currency=EUR/filename
    """

    bucket: str
    prefix: str
    filename: str

    def construct_path(self, partition_path: Optional[str] = None) -> str:
        """Constructs the cloud storage path for a file."""

        if partition_path:
            return f"gs://{self.bucket}/{self.prefix}/{partition_path}/{self.filename}"
        else:
            return f"gs://{self.bucket}/{self.prefix}/{self.filename}"


@dataclass(kw_only=True)
class LocalFile(PartitionedFileTarget, Target):
    """
    Target that creates files on the local file system

    Supports csv and parquet `filetype`s.

    Usage:

        targets:
        - target: LocalFile
          filetype: csv / parquet
          filepath: path/to/myfile # an absolute or relative base path
          filename: myfile.csv # the name of the file

          # Optional params
          partition_cols: [col1, col2] # Optional. The columns within the dataset to partition on.


    If partition_cols is specified then data will be split into separate files and
    separate files / directories will be created with filepaths that follow the hive partitioning structure.
    e.g. If a dataset has dt and currency columns and these are specified as partition_cols
    then you might expect the following files to be created:
    - filepath/dt=2022-01-01/currency=USD/filename
    - filepath/dt=2022-01-01/currency=EUR/filename
    """

    filepath: str
    filename: str

    def construct_path(self, partition_path: Optional[str] = None) -> str:
        """Constructs the filepath for a local file."""

        if partition_path:
            return f"{self.filepath}/{partition_path}/{self.filename}"
        else:
            return f"{self.filepath}/{self.filename}"


    def pre_save_object(self, path: str) -> None:
        """Before saving files check and create any dirs."""

        if not os.path.exists(os.path.dirname(path)):
            logging.debug(f"creating dir {os.path.dirname(path)}")
            os.makedirs(os.path.dirname(path), exist_ok=True)





@dataclass(kw_only=True)
class BigQuery(Target):
    """
    Target that loads data to BigQuery tables.

    This will create datasets / tables that don't currently exist, or load data to existing tables.

    Usage:

        targets:
        - target: BigQuery
          dataset: mydataset # the name of the dataset where the table belongs
          table: mytable # the name of the table to load to

          # Optional parameters
          project: myproject # the GCP project where the dataset exists defaults to the system default
          truncate: True # whether to clear the table before loading, defaults to False
          post_generation_sql: "INSERT INTO xxx" # A query that will be run after the data has been inserted
    """

    project: str | None = None
    dataset: str
    table: str
    truncate: bool = False
    post_generation_sql: str | None = None
    client = None
    bigquery = None

    def setup(self):
        """Setup the BQ client for the target."""

        from google.cloud import bigquery
        self.bigquery = bigquery

        if not self.project:
            self.project = GOOGLE_PROJECT_ID

        if not self.client:
            self.client = bigquery.Client(self.project)



    def get_or_create_dataset(self, dataset_id: str):
        """Check whether the dataset exists or create if not."""

        try:
            dataset = self.client.get_dataset(dataset_id)
        except Exception as e:
            logging.error(e)
            logging.info(f"Dataset {dataset_id} does not exist. Creating.")
            dataset = self.bigquery.Dataset(dataset_id)
            dataset.location = 'europe-west2'
            dataset = self.client.create_dataset(dataset)
        return dataset

    def save(self, tbl):
        """The save method is called when this target is executed."""
        self.setup()

        dataset_id = f"{self.project}.{self.dataset}"
        schema_table = f"{self.project}.{self.dataset}.{self.table}"
        dataset = self.get_or_create_dataset(dataset_id)

        job_config = None

        if self.truncate:
            job_config = self.bigquery.LoadJobConfig(
                write_disposition=self.bigquery.WriteDisposition.WRITE_TRUNCATE)

        logging.info(f"Uploading {tbl.name} data to {schema_table}")
        result = self.client.load_table_from_dataframe(
            tbl.df, schema_table, job_config=job_config).result()

        if self.post_generation_sql and result.state == "DONE":
            self.client.query(self.post_generation_sql.format(t=self),
                              project=self.project).result()

        logging.info(
            f"Result: {result.state} {result.output_rows} rows written to {result.destination}"
        )


@dataclass(kw_only=True)
class StreamingTarget(Target):
    """Base class for targets that send data to streaming systems."""

    @abstractmethod
    def process_row(self, row, row_attrs):
        pass

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def save(self, tbl):
        pass



@dataclass(kw_only=True)
class Pubsub(StreamingTarget, Target):
    """
    Target that publishes data to Pubsub.

    This target converts the data into json format and publishes each row as a separate pubsub message.
    It expects the topic to already exist.

    Usage:

        targets:
        - target: Pubsub
          topic: mytopic # the name of the topic

          # Optional parameters
          project: myproject # the GCP project where the topic exists defaults to the system default
          output_cols: [col1, col2] # the columns to convert to json and use for the message body
          attribute_cols: [col3, col4] # the columns to pass as pubsub message attributes, these columns will be removed from the message body unless they are also specified in the output_cols
          attributes: # additional attributes to add to the pbsub messages
            key1: value1
            key2: value2

          delay: 0.01 # the time in seconds to wait between each publish, default is 0.01
          date_format: iso # how timestamp fields should be formatted in the json eith iso or epoch
          time_unit: s # the resolution to use for timestamps, s, ms, us etc.
    """

    topic: str
    project: Optional[str] = None

    output_cols: list[str] = field(default_factory=list)
    attribute_cols: list[str] = field(default_factory=list)
    attributes: dict[str,str] = field(default_factory=dict)

    delay: float = 0.01
    date_format: str = 'iso' # or epoch
    time_unit: str = 'ms'
    validate_first: bool = True
    client = None

    def __post_init__(self):
        if not self.project:
            self.project = GOOGLE_PROJECT_ID

    @property
    def topic_path(self):
        return f"projects/{self.project}/topics/{self.topic}"

    def setup(self):
        from google.cloud import pubsub_v1

        if not self.client:
            self.client = pubsub_v1.PublisherClient()

    def process_row(self, row, row_attrs):
        return self.client.publish(self.topic_path, row.encode(), **row_attrs, **self.attributes)

    def process_df(self, df) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        if self.attribute_cols:
            attributes_df = df[self.attribute_cols].astype('string')
        else:
            attributes_df = None

        if self.output_cols:
            data_df = df[self.output_cols]
        else:
            data_df = df.drop(self.attribute_cols, axis=1)

        return data_df, attributes_df



    def save(self, tbl):
        self.setup()

        data_df, attributes_df = self.process_df(tbl.df)

        json_data = data_df.to_json(
            orient='records',
            lines=True,
            date_format=self.date_format,
            date_unit=self.time_unit).strip().split("\n")

        for i, row in enumerate(json_data):

            if attributes_df is not None:
                row_attrs = attributes_df.iloc[i].to_dict()
            else:
                row_attrs = None

            if self.validate_first:
                res = self.process_row(row, row_attrs)
                logging.info(f"publishing first message to topic [{self.topic_path}]" \
                    f" with data: [{row}]" \
                    f" and attributes: [{row_attrs}]" \
                    f"message_id: {res.result()}")

                self.validate_first = False
            else:
                res = self.process_row(row, row_attrs)

            if self.delay > 0:
                time.sleep(self.delay)
