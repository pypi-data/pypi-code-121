"""
This module defines the exceptions used throughout this package
"""
from dataclasses import dataclass


@dataclass
class S3BucketLocation:
    """
    Class that contains information about objects location in s3.

    args:
        source_bucket (str): The bucket where objects are located.
        source_prefix (str): The prefix (ie 'folder') where the objects are located.
        destination_bucket (str): The bucket where the copy-to destination is located
        destination_prefix (str): The prefix (ie 'folder') where the copy-to destination is located
    """

    source_bucket: str
    source_prefix: str
    destination_bucket: str
    destination_prefix: str


class DaiError(Exception):
    """Base class for exceptions in DAI."""


class DaiS3Error(DaiError):
    """Base class for exceptions related to S3."""


class DaiS3CopyObjectError(DaiS3Error):
    """Class for exceptions related to copying objects in S3."""
    def __init__(self, s3_bucket_location: S3BucketLocation, message=None):  # pylint: disable=super-init-not-called
        self.source = f"s3://{s3_bucket_location.source_bucket}/{s3_bucket_location.source_prefix}"
        self.destination = f"s3://{s3_bucket_location.destination_bucket}/{s3_bucket_location.destination_prefix}"
        self.message = message

    def __repr__(self):
        ret_str = f"source: {self.source}, destination: {self.destination}"
        if self.message:
            ret_str += f"\nError message: {self.message}"

        return ret_str

    def __str__(self):
        ret_str = f"Error at copying: {self.source} -> {self.destination}"
        if self.message:
            ret_str += f"\nError message: {self.message}"

        return ret_str


class DaiS3DeleteObjectError(DaiS3Error):
    """Class for exceptions related to deleting objects in S3."""

    def __init__(self, s3_bucket: str, error_infos: list, message: str = None):  # pylint: disable=super-init-not-called
        self.bucket = s3_bucket
        self.error_infos = error_infos
        self.message = message

    def __repr__(self):
        ret_str = f"Bucket: {self.bucket}, Error info: {self.error_infos}"
        if self.message:
            ret_str += f"\nError message: {self.message}"

        return ret_str

    def __str__(self):
        ret_str = f"Error at deleting objects in bucket {self.bucket}."
        if self.message:
            ret_str += f"\nError message: {self.message}"
        ret_str += "\nAdditional information about failed removals: \n"
        as_str = [f"{error_info}" for error_info in self.error_infos]
        ret_str += '\n'.join(as_str)

        return ret_str


class DaiInputError(DaiError):
    """Base class for exceptions related to input data in DAI."""


class MissingInputError(DaiInputError):
    """Exception raised when missing critical input information.

    Attributes:
        missing_inputs -- list of missing inputs
        message -- explanation of the error
    """

    def __init__(self, inputs_list, message):  # pylint: disable=super-init-not-called
        self.inputs_list = inputs_list
        self.message = message

    def __repr__(self):
        ret_str = f"Missing inputs: {self.inputs_list}"
        ret_str += f"\nError message: {self.message}"

        return ret_str

    def __str__(self):
        ret_str = f"The following inputs are missing: {self.inputs_list}"
        ret_str += f"\nError message: {self.message}"

        return ret_str


class IncorrectInputValueError(DaiInputError):
    """Exception raised when incorrect input(s) provided.

    Attributes:
        input_dict -- dictionary providing the name and values of the inputs containing incorrect values.
        message -- explanation of the error
    """

    def __init__(self, incorrect_inputs_dict, message):  # pylint: disable=super-init-not-called
        self.incorrect_inputs_dict = incorrect_inputs_dict
        self.message = message

    def __repr__(self):
        ret_str = f"Incorrect inputs: {self.incorrect_inputs_dict}"
        ret_str += f"\nError message: {self.message}"

        return ret_str

    def __str__(self):
        ret_str = f"The following input(s) received incorrect value(s): {self.incorrect_inputs_dict}"
        ret_str += f"\nError message: {self.message}"

        return ret_str
