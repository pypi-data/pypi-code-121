import logging
from typing import List
from abc import ABC, abstractmethod

import pandas as pd
from minio import Minio
from minio.commonconfig import Tags

from miniops.utils import log_memory_usage

class MinioAgent(ABC):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool,
        name: str,
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.name = name
        if secure:
            self.hostname = f"https://{endpoint}"
        else:
            self.hostname = f"http://{endpoint}"

    @abstractmethod
    def process(self, dataframe: pd.DataFrame):
        pass

    def preprocess(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        # by default this does not do anything, implement your own if needed
        return dataframe

    def process_generator(self, dataframe_generator, preprocessing: bool = True):
        for counter, dataframe in enumerate(dataframe_generator):
            logging.info(
                f"processing dataframe #{counter+1}, with {len(dataframe)} items"
            )
            log_memory_usage()
            if preprocessing:
                dataframe = self.preprocess(dataframe)
            self.process(dataframe)

    def get_object_names_generator_for_objects_in_bucket(self, **kwargs):
        pointers = self.client.list_objects(**kwargs)
        for pointer in pointers:
            yield pointer._object_name

    def get_object_names_from_bucket(self, bucket_name: str) -> List[str]:
        names_generator = self.get_object_names_generator_for_objects_in_bucket(
            bucket_name=bucket_name, recursive=True
        )
        return [name for name in names_generator]

    def get_df_generator_for_objects_in_bucket(
        self, names: List[str], bucket_name: str
    ):
        if not bucket_name:
            bucket_name = self.data_bucket
        for name in names:
            dataframe = pd.read_json(
                f"{self.hostname}/{bucket_name}/{name}", lines=True
            )
            yield dataframe

    def has_object_not_been_analysed(self, object_name: str, bucket_name: str) -> bool:
        tags = self.client.get_object_tags(bucket_name, object_name)
        if not tags or tags[f"{self.name}-processed"] == "False":
            return True
        else:
            return False

    def filter_objects_todo(
        self, object_names: List[str], bucket_name: str
    ) -> List[str]:
        return list(
            filter(
                lambda name: self.has_object_not_been_analysed(name, bucket_name),
                object_names,
            )
        )

    def tag_objects_as_processed(
        self, object_names_processed: List[str], bucket_name: str
    ) -> None:
        for obj_name in object_names_processed:
            tags = Tags.new_object_tags()
            tags[f"{self.name}-processed"] = "True"
            self.client.set_object_tags(bucket_name, obj_name, tags)

    def run(self, bucket_name: str, dry_run: bool = False):
        object_names_all = self.get_object_names_from_bucket(bucket_name=bucket_name)
        logging.debug(f"objects in bucket: {object_names_all}")
        object_names_todo = self.filter_objects_todo(
            object_names=object_names_all, bucket_name=bucket_name
        )
        logging.info(f"objects to do: {object_names_todo}")
        df_generator = self.get_df_generator_for_objects_in_bucket(
            names=object_names_todo, bucket_name=bucket_name
        )
        self.process(df_generator)
        if not dry_run:
            self.tag_objects_as_processed(
                object_names_processed=object_names_todo, bucket_name=bucket_name
            )
