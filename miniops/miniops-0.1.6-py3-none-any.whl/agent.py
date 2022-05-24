import logging
import time
from typing import List, Optional
from abc import ABC, abstractmethod
from unittest import skip
from urllib.error import HTTPError

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

    def process_generator(self, dataframe_generator, object_names: List[str]) -> List[str]:
        skipped = []
        for counter, dataframe in enumerate(dataframe_generator):
            logging.info(
                f"processing dataframe #{counter+1}, with {len(dataframe)} items"
            )
            if dataframe is not None:
                log_memory_usage()
                self.process(dataframe)
            else:
                skipped.append(object_names[counter])
        return skipped

    def get_object_names_generator_for_objects_in_bucket(self, **kwargs):
        pointers = self.client.list_objects(**kwargs)
        for pointer in pointers:
            yield pointer._object_name

    def get_object_names_from_bucket(self, bucket_name: str) -> List[str]:
        names_generator = self.get_object_names_generator_for_objects_in_bucket(
            bucket_name=bucket_name, recursive=True
        )
        return [name for name in names_generator]

    def try_to_read_dataframe_from_minio(
        self, bucket_name, object_name, max_retries: int = 2, timeout_seconds: int = 10
    ) -> Optional[pd.DataFrame]:
        for counter in range(max_retries):
            try:
                dataframe = pd.read_json(
                    f"{self.hostname}/{bucket_name}/{object_name}", lines=True
                )
                return dataframe
            except HTTPError:
                first_sentence = f"Could not read {object_name} from {bucket_name}, attempt: {counter+1}."
                if counter < max_retries:
                    logging.error(
                        f"{first_sentence} Trying again in {timeout_seconds}..."
                    )
                    time.sleep(timeout_seconds)
                else:
                    logging.error(f"{first_sentence} Giving up")

    def get_df_generator_for_objects_in_bucket(
        self, names: List[str], bucket_name: str = None
    ):
        if not bucket_name:
            bucket_name = self.data_bucket
        for name in names:
            dataframe = self.try_to_read_dataframe_from_minio(
                bucket_name=bucket_name, object_name=name
            )
            if dataframe is not None:
                dataframe = self.preprocess(dataframe)
                yield dataframe
            else:
                yield None

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
        skipped = self.process_generator(df_generator, object_names=object_names_todo)
        logging.debug(f"skipped objects: {skipped}")
        done = list(set(object_names_todo) - set(skipped))
        if not dry_run:
            self.tag_objects_as_processed(
                object_names_processed=done, bucket_name=bucket_name
            )
        logging.info(f"skipped {len(skipped)} / {len(object_names_todo)} objects")
        logging.critical("DONE")
