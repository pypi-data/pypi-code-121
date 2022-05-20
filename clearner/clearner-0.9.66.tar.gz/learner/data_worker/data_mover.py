# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements classes and functions related to moving data around. This would include moving data to/from
GPU, S3, etc."""
import logging
import sys
import os

import torch
import boto3
from pathlib import Path

from learner.configuration.configuration import Configuration


class DataMoverManager:
    """This class handles the operations related to moving the data around. One example include uploading/downloading
    data to/from S3. In the future, we may add some other functionalities such as SFTP, etc. This class does not
    handle the implementation, instead it uses other classes to do the work."""

    def __init__(self, conf: Configuration):
        """Instantiate a DataMoverManager object using a conf object

        :param conf: an instance of the Configuration class
        """
        self._conf = conf
        self.data_mover = S3DataMover()

    @property
    def conf(self):
        return self._conf

    def move_data(self, mode):
        """Call the necessary methods to move data around depending on the mode. Currently, we only move data to and
        from s3 but in the future we may add other options.

        :param mode: the mode for moving data, it could be "download" or "upload"
        :return: None
        """
        if self.conf.workspace.s3_activate and mode == "download":
            self.data_mover.download_folder_from_s3(self.conf.workspace.s3_path, self.conf.workspace.path)
        if self.conf.workspace.s3_activate and mode == "upload":
            self.data_mover.upload_folder_to_s3(self.conf.workspace.path, self.conf.workspace.s3_path)


class S3DataMover:
    """This class implements method that move data to or from S3. This class only implements methods that we currently
    need.
    """
    def __init__(self):
        """Instantiate an S3DataMover object.
        """
        self._s3_client = boto3.client("s3")

    @property
    def client(self):
        return self._s3_client

    def upload_file_to_s3(self, from_file, to_file):
        """Upload a file to a s3 location. This method is used by copy_folder_to_s3 method.

        :param from_file: full path to the local file
        :param to_file:  full path to the s3 location
        :return: None
        """
        bucket, s3_key = split_s3_path(to_file)

        self._s3_client.upload_file(from_file, bucket, s3_key)

    def upload_folder_to_s3(self, from_folder, to_folder, pattern="*"):
        """Upload a local folder recursively to s3. We currently do not upload the empty folders.

        :param from_folder: a local folder
        :param to_folder: a s3 "folder"
        :param pattern: regular expression pattern passed to "glob" to filter the type of files needed.
        :return: None
        """
        logging.info("Uploading data to s3...")
        bucket, s3_key = split_s3_path(to_folder)
        s3_folder = Path(s3_key)
        parent_folder = Path(from_folder)
        for item in parent_folder.glob(pattern):
            relative = item.relative_to(parent_folder)
            target_full_path = "s3://{}/{}".format(bucket, s3_folder.joinpath(relative))
            if item.is_file():
                self.upload_file_to_s3(str(item), target_full_path)
            else:
                self.upload_folder_to_s3(str(item), target_full_path)
        logging.info("Successfully uploaded data to s3.")

    def download_folder_from_s3(self, from_folder, to_folder):
        """Download all the objects inside a "folder" recursively from s3.

        :param from_folder: the full path to the "folder" on s3.
        :param to_folder: the full path to the local folder to download the objects into
        :return: None
        """
        logging.info("Downloading data from s3...")
        bucket, s3_key = split_s3_path(from_folder)
        # if the folder is empty we return
        if 'Contents' not in self._s3_client.list_objects(Bucket=bucket, Prefix=s3_key):
            logging.info("The s3 location is empty.")
            return
        for key in self._s3_client.list_objects(Bucket=bucket, Prefix=s3_key)['Contents']:
            s3_parent_folder = Path(s3_key)
            relative_path = Path(key['Key']).relative_to(s3_parent_folder)
            target_folder = Path(to_folder)
            full_path = target_folder.joinpath(relative_path)
            if key['Key'].endswith('/'):
                if not os.path.exists(full_path):
                    os.makedirs(full_path)
            else:
                directory = full_path.parents[0]
                if not os.path.exists(directory):
                    os.makedirs(directory)
                self._s3_client.download_file(bucket, key['Key'], str(full_path))
        logging.info("Successfully downloaded data from s3.")

    def delete_from_s3(self, s3_path: str):
        """delete all objects in given s3_path

        :param s3_path: location to the s3 object. e.g. s3://my-awesome-bucket/path/to/object
        :return: None
        """
        bucket, s3_key = split_s3_path(s3_path)
        # if the folder is empty we return
        if 'Contents' not in self._s3_client.list_objects(Bucket=bucket, Prefix=s3_key):
            return
        for key in self._s3_client.list_objects(Bucket=bucket, Prefix=s3_key)['Contents']:
            self._s3_client.delete_object(Bucket=bucket, Key=key['Key'])


def move_to_device(data, device):
    """Move the data (a single or a list of PyTorch tensors) to a specific device. The device would be cpu or cuda. We
    currently are not validating the devices because device is validated when instantiating the conf object. The reason
    for implementing this method is that in some cases, we have a list of tensors that need to be moved instead of
    a single tensor. This function can handle those cases as well.

    :param data: the data (mainly a PyTorch tensor or a list of PyTorch tensors)
    :param device: the name of the device, could be "cpu" or "cuda"
    :return: the same data in that device.
    """
    if isinstance(data, torch.Tensor):
        return data.to(device)
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = data[i].to(device)
        return data


def split_s3_path(s3_path):
    """Split the s3_path into s3 key and bucket. The result will all be lower case.

    Example:
    >>> bucket, s3_key = split_s3_path("s3://bucket/path/to/object")
    >>> bucket
    'bucket'
    >>> s3_key
    'path/to/object'

    :param s3_path: a full s3 path to an object, e.g. s3://bucket/path/to/object
    :return: a tuple of strings, (bucket, s3_key)
    """
    if not s3_path.startswith("s3://"):
        logging.critical("The S3 path should start with 's3://'. Exiting...")
        sys.exit(1)

    s3_path = s3_path[5:]
    bucket, s3_key = s3_path.split("/", 1)
    return bucket, s3_key
