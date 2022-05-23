# pylint: disable=too-few-public-methods

"""
    CUSTOM WRITER CLASSES
"""
import json
import os
from datetime import datetime

import boto3


class CustomS3JsonWriter:
    """Class Extends Basic LocalGZJsonWriter"""

    def __init__(self, bucket, file_path, profile_name=None):
        self.bucket = bucket
        self.file_path = file_path

        self.profile_name = profile_name

        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)

        self.s3_resource = self.boto3_session.resource("s3")

    def write_to_s3(self, json_data):
        """
        Writes json data to s3 and names it by
        date of writing.
        """
        now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        key_path = f"{os.path.join(self.file_path, now)}.json"

        self.s3_resource.Object(self.bucket, key_path).put(Body=json.dumps(json_data))

    def write_partition_to_s3(self, json_data):
        """
        Partitions data by date to reduce duplication in s3.
        So the plan is to ensure that if we:
            - pull from a specific date, we overwrite all that days data in the buckets.
            - this way, we ensure all data is original and in its most updated state.
        """
        for dimension, dimension_dataset in json_data.items():
            partition_dataset = {}
            for row in dimension_dataset:
                date_value = row.get("date")

                if date_value not in partition_dataset:
                    partition_dataset[date_value] = []
                partition_dataset[date_value].append(row)

            for partition_key, partition_data in partition_dataset.items():
                key_path = f"{self.file_path}/{dimension}/{partition_key.replace('-', '')}.json"
                print(f"Writing data to {key_path}.")
                self.s3_resource.Object(self.bucket, key_path).put(
                    Body=json.dumps(partition_data)
                )
