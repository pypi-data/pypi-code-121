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

    def write_partition_to_s3(self, json_data):
        """
        Partitions data by date to reduce duplication in s3.
        So the plan is to ensure that if we:
            - pull from a specific date, we overwrite all that days data in the buckets.
            - this way, we ensure all data is original and in its most updated state.
        """
        partition_dataset = {}
        for row in json_data:
            # each stat has its own relevant date field
            date_value = row.get("completed_at", row.get("created_at_date"))
            if date_value not in partition_dataset:
                partition_dataset[date_value] = []
            partition_dataset[date_value].append(row)

        for date, date_dataset in partition_dataset.items():
            key_path = f"{self.file_path}/{date}.json"
            # only write if there is data
            if len(date_dataset) > 0:
                print(f"Writing data to {key_path}.")
                self.s3_resource.Object(self.bucket, key_path).put(
                    Body=json.dumps(date_dataset)
                )

    def write_to_s3(self, data, extension):
        """
        Writes json data to s3 and names it by
        date of writing.
        """
        if extension not in ["json", "csv", "json.gz", "csv.gz"]:
            raise ValueError(f"Param: {extension} is not a valid option for extension.")

        now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        key_path = f"{os.path.join(self.file_path, now)}.{extension}"

        self.s3_resource.Object(self.bucket, key_path).put(Body=data)
