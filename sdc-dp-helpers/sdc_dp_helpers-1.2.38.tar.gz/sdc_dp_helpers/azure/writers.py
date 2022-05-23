"""
    CUSTOM WRITER CLASSES
        - Class which manages writer tasks like
        auth, write metadata, write file, create dir structure
"""
import json
import os
from datetime import datetime, timedelta

import boto3

from sdc_dp_helpers.base_writer import CustomLocalJsonWriter


class CustomS3JsonWriter(CustomLocalJsonWriter):
    """Class Extends Basic LocalJsonWriter"""

    def __init__(
        self,
        file_name: str,
        folder_path: str,
        bucket: str,
        profile_name: str = None,
        **kwargs
    ):
        self.os_path_sep = "/"

        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)

        self.bucket = bucket
        self.file_name = file_name
        """Writes a general object to s3"""
        self.s3_resource = self.boto3_session.resource("s3")
        super().__init__(file_name=file_name, folder_path=folder_path, **kwargs)
        self.metadata_file = kwargs.get("metadata_file", "metadata.json.gz")

    def set_full_path(self):
        """Set full path to write to, using the .net ticker filename value."""
        # creates full path
        date_prefix = self.file_name.split(".")[0].split("_")[-1]
        date_prefix = (
            datetime(1, 1, 1) + timedelta(microseconds=int(date_prefix) // 10)
        ).strftime("%Y/%m/%d")

        full_path = [date_prefix, self.folder_path]

        return os.path.join(*full_path).replace("\\", "/")

    # pylint: disable=no-member,too-many-arguments
    def write_to_s3(self, json_data, data_path):
        """
        Write report to s3 bucket
        """
        json_data = json.dumps(json_data)
        self.s3_resource.Bucket(self.bucket).put_object(
            Key=os.path.join(self.full_path, data_path).replace("\\", "/"),
            Body=json_data,
        )

    def write_file(self, data: dict):
        """
        upload python dict into s3 bucket with gzip archive
        """
        # create directory structure if not exists
        self.full_path = self.set_full_path()

        # generate a unix timestamp suffix for file
        self.data = data
        suff = self.timestamp_suffix()
        data_path = "{}_{}.json".format(self.file_name, suff)
        self.write_to_s3(self.data, data_path)
        self.data = []
