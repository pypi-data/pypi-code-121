# pylint: skip-file
# File skipped because the refactoring will be complex and requires a new ticket
import datetime
import os
import urllib.parse
from enum import Enum, auto
from io import BytesIO
from typing import Any, Dict, Optional
from urllib.parse import unquote_plus
from zipfile import BadZipFile, ZipFile

from botocore.exceptions import ClientError

import dai_python_commons.dai_error as dai_error
from dai_python_commons.dai_error import DaiError
from dai_python_commons.dai_error import S3BucketLocation
from dai_python_commons.s3_utils import S3Utils


class ObjectEqualityStrategy(Enum):
    ETAG = auto()
    SIZE = auto()


class S3EventObjectCopy:
    """
    Class that provides functionality to copy objects that triggered an S3 event from one bucket to another
    Useful in lambda functions that have an S3 trigger on PUT operations
    """

    def __init__(self, s3_resource, logger, destination_bucket: str, source_prefix_to_replace: str,
                 destination_prefix_replacement: str, unzip_file: bool, filename_prefix: str = '',
                 remove_processed: bool = False,
                 object_equality_strategy: ObjectEqualityStrategy = ObjectEqualityStrategy.ETAG):
        """
        :param s3_resource: Boto3 resource for S3
        :param logger: The logger
        :param destination_bucket: The name of the destination bucket
        :param source_prefix_to_replace: A part of the prefix in the source bucket that should be replaced with another
        value in the destination.
        :param destination_prefix_replacement: A prefix that should replace source_prefix_to_replace at the destination
        bucket. If for example, we should copy an object source_bucket/A/B/C/x.txt to destination_bucket, and
        source_prefix_to_replace = "/A/B/", destination_prefix_replacement = "E/", then the object will be copied at
        destination_bucket/E/C/x.txt"
        :param unzip_file: Whether the file should be unzipped
        :param filename_prefix: A string that will be put as prefix at the destination, for example:
        "x.txt" --> "<prefix>_x.txt"
        :param remove_processed: Whether the file should be removed from the source bucket after processing. Note that
        this option is not supported when unzip_file = True, or for files larger than 4.9 Gb.
        The file is removed only if the processing was successful
        :param object_equality_strategy: If ETAG or SIZE should be used to measure the equality when removing
        processed objects. ETAG is more accurate but doesn't always work, SIZE is the next best thing.
        """
        self.s3_resource = s3_resource
        self.s3_client = self.s3_resource.meta.client
        self.logger = logger
        self.destination_bucket = destination_bucket
        self.source_prefix_to_replace = source_prefix_to_replace
        self.destination_prefix_replacement = destination_prefix_replacement
        self.unzip_file = unzip_file
        self.filename_prefix = filename_prefix
        self.remove_processed = remove_processed
        self.object_equality_strategy = object_equality_strategy
        if self.remove_processed and self.unzip_file:
            raise dai_error.IncorrectInputValueError(
                {"unzip_file": unzip_file, "remove_unprocessed": remove_processed},
                "The remove_unprocessed option is not supported together with unzip_file.")

    @staticmethod
    def service_exception(response: dict) -> bool:
        """
        Given a response from a boto3 S3 client command, check if a service error occurred

        :param response: Response from an S3 client request
        :return: True if an error occurred, False otherwise
        """
        if "Error" in response:
            return True

        if "ResponseMetadata" in response and "HTTPStatusCode" in response["ResponseMetadata"] and \
                response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return True

        return False

    @staticmethod
    def extract_field_from_dict(the_dict: dict, field_name: str):
        """
        Extract a specific field from a dictionary

        :param the_dict: dictionary
        :param field_name: field to be extracted
        :return: The value of field_name in the_dict or None if the field is not found in the dictionary
        """
        if the_dict and field_name in the_dict:
            return the_dict[field_name]

        return None

    def are_equal(self, object1_info: dict, object2_info: dict) -> bool:
        if self.object_equality_strategy is ObjectEqualityStrategy.ETAG:
            return S3EventObjectCopy.are_etags_identical(object1_info, object2_info)
        elif self.object_equality_strategy is ObjectEqualityStrategy.SIZE:
            return S3EventObjectCopy.are_objects_same_size(object1_info, object2_info)
        else:
            raise ValueError(f"Unknown object equality strategy: {self.object_equality_strategy}")

    @staticmethod
    def are_etags_identical(object1_info: dict, object2_info: dict) -> bool:
        """
        Given two dictionaries as returned by S3 method list_objects_v2, check if their ETags are identical

        :param object1_info: Dictionary as returned by list_objects_v2
        :param object2_info: Dictionary as returned by list_objects_v2
        :return: True if the ETags are identical, False otherwise
        """
        etag1 = S3EventObjectCopy.extract_field_from_dict(object1_info, "ETag")
        etag2 = S3EventObjectCopy.extract_field_from_dict(object2_info, "ETag")
        if not etag1 or not etag2 or etag1 != etag2:
            return False

        return True

    @staticmethod
    def are_objects_same_size(object1_info: dict, object2_info: dict) -> bool:
        """
        Given two dictionaries as returned by S3 method list_objects_v2, check if they are the same size

        :param object1_info: Dictionary as returned by list_objects_v2
        :param object2_info: Dictionary as returned by list_objects_v2
        :return: True if the objects have the same size, False otherwise
        """
        size1 = S3EventObjectCopy.extract_field_from_dict(object1_info, "Size")
        size2 = S3EventObjectCopy.extract_field_from_dict(object2_info, "Size")
        if size1 is None or size2 is None:
            return False

        return size1 == size2

    @staticmethod
    def get_object_lock_retain_until_date(tag_dict: Dict[str, any]) -> Optional[datetime.datetime]:
        """
        Calculates the object lock retain until date based on the *retention_time* tag value

        :param tag_dict: dict that may contain the *retention_time* key
        :return: the "retain until date" or None if no *retention_time* can be found in *destination_tags*
        """

        if tag_dict is not None and "retention_time" in tag_dict:
            nr_days = int(tag_dict["retention_time"])
            if nr_days > 0:
                return datetime.datetime.now() + datetime.timedelta(days=nr_days)
            else:
                raise DaiError("Retention time must be greater than 0 days!")

        return None

    def _unzip_and_copy(self, source_bucket_name: str, source_object: str, destination_prefix_wo_filename: str):
        """
        Unzip a file and copy to destination without persisting to disk

        :param source_bucket_name: The bucket where the zip file is located
        :param source_object: The full name of the zip file in the source bucket
        :param destination_prefix_wo_filename: The prefix in the destination bucket, excluding the filename
        :return:
        """
        self.logger.debug(f"Unzip {source_bucket_name}/{source_object} and copy all files to"
                          f" {self.destination_bucket}/{destination_prefix_wo_filename}")
        # read the zipfile as bytes in memory
        zip_obj = self.s3_resource.Object(bucket_name=source_bucket_name, key=source_object)
        buffer = BytesIO(zip_obj.get()["Body"].read())

        # iterate over the files in the zip and copy them to the destination bucket
        zip_file = ZipFile(buffer)
        for filename in zip_file.namelist():
            # create the full prefix
            new_filename = self._append_filename_prefix(filename)
            destination_prefix = os.path.join(destination_prefix_wo_filename, new_filename)
            # upload the object
            self.logger.debug(f"{filename} -> {destination_prefix}")
            self.s3_client.upload_fileobj(zip_file.open(filename), Bucket=self.destination_bucket,
                                          Key=destination_prefix)

    def _get_object_info(self, bucket: str, prefix: str) -> Dict[str, Any]:
        """
        Return metadata information about an object stored in S3

        :param bucket: name of the bucket
        :param prefix: prefix of the object
        :return: A dictionary as returned by list_objects_v2, or None if the object doesn't exist
        """
        result = None
        try:

            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            # get first element in Contents list
            result = next(iter(response.get("Contents", [])), None)
        # The boto3 exception mechanisms seems pretty badly documented so I use Exception to be on the safe side
        except Exception as the_exception:
            self.logger.opt(exception=True).warning(
                f"Unable to get information about object {bucket}/{prefix}, error: {the_exception}")

        return result

    def _remove_processed_object(self, source_bucket: str, source_prefix: str, source_object_info: Dict[str, Any],
                                 destination_object_info: Dict[str, Any]) -> bool:
        """
        Removes an object that has been processed. It only removes the object if the source and destination etags
        match

        :param source_bucket: The name of the source bucket
        :param source_prefix: The key of the object
        :param source_object_info: Metadata information about the source object as returned by boto3 list_objects_v2
        :param destination_object_info: Metadata information about the destination object as returned by boto3
         list_objects_v2
        :return: True if the object was deleted successfully, False otherwise
        """
        self.logger.debug(f"Attempting to delete processed object {source_bucket}/{source_prefix}")

        source_object = f"{source_bucket}/{source_prefix}"

        # if the objects are not equal the source object is not removed
        if not self.are_equal(source_object_info, destination_object_info):
            self.logger.warning(f"Source and destination objects do not match, the processed object "
                                f"{source_object} will not be removed")
            return False

        # delete the processed file
        try:
            _response = self.s3_client.delete_object(Bucket=source_bucket, Key=source_prefix)
        except Exception as the_exception:
            self.logger.opt(exception=True).warning(f"Unable to remove {source_object}, error: {the_exception}")
            return False
        else:
            self.logger.debug(f"Object {source_object} was deleted")
            return True

    def _get_destination_prefix(self, source_prefix: str, exclude_filename: bool = False) -> str:
        """
        Gets the destination prefix for a given source prefix

        :param source_prefix The source prefix of the object
        :param exclude_filename: Whether the 'filename' should be excluded from the prefix
        :return: The prefix of the object at the destination
        """
        destination_prefix_wo_filename = os.path.dirname(source_prefix)
        if self.source_prefix_to_replace is not None:
            destination_prefix_wo_filename = destination_prefix_wo_filename.replace(
                self.source_prefix_to_replace.strip("/"), self.destination_prefix_replacement.strip("/"))

        if exclude_filename:
            return destination_prefix_wo_filename

        filename = self._append_filename_prefix(os.path.basename(source_prefix))

        return os.path.join(destination_prefix_wo_filename, filename)

    def _append_filename_prefix(self, filename: str):
        """
        If a filename prefix is configured it will be added to the given filename.

        Examples::
            foo.txt     --> <filename_prefix>_foo.txt

        :param filename: the filename that should have the prefix added to it (no 'folder' path)
        :return: the filename with prefix added, if filename prefix configured, else same as given filename
        """
        if self.filename_prefix:
            filename = f'{self.filename_prefix}_{filename}'

        return filename

    def _get_tagging_str(self, tag_dict: Dict[str, any]) -> str:
        """
        :param tag_dict: Dictionary giving tag_name, tag_value
        :return: A string that can be used by boto3 copy commands to tag objects
        """
        return urllib.parse.urlencode(tag_dict) if tag_dict else ""

    def _copy_using_unmanaged_transfer(self,
                                       source_bucket_name: str,
                                       source_object: str,
                                       copy_source_object: Dict[str, any],
                                       object_info: Dict[str, Any],
                                       destination_prefix: str,
                                       destination_tags: Dict[str, any]):
        """
        Uses client.copy_object to copy an object from one location to another.

        :param source_bucket_name: The name of the source bucket
        :param source_object: Key of the object to be copied
        :param copy_source_object: Dict containing information about the source bucket and key
        :param object_info: Dictionary as returned by list_objects_v2
        :param destination_prefix: The destination prefix
        :param destination_tags: Tags that should be set on the object in the request.
        :return:
        """
        tagging = self._get_tagging_str(destination_tags)

        object_lock_arguments = {}
        if S3Utils.is_raw_bucket(self.destination_bucket):
            if destination_tags.get("retention_type") in ["shall", "may"]:
                object_lock_arguments = {
                    "ObjectLockMode": "GOVERNANCE",
                    "ObjectLockRetainUntilDate": self.get_object_lock_retain_until_date(destination_tags)
                }
            elif destination_tags.get("retention_type") == "preserve":
                # 52000 weeks are ~1000 years
                object_lock_arguments = {
                    "ObjectLockMode": "GOVERNANCE",
                    "ObjectLockRetainUntilDate": datetime.datetime.now() + datetime.timedelta(weeks=52000)
                }
        response = self.s3_client.copy_object(CopySource=copy_source_object,
                                              Bucket=self.destination_bucket,
                                              Key=destination_prefix,
                                              Tagging=tagging,
                                              TaggingDirective="REPLACE",
                                              **object_lock_arguments
                                              )

        # check if the copying was successful
        s3_bucket_location = S3BucketLocation(source_bucket_name,
                                              source_object,
                                              self.destination_bucket,
                                              destination_prefix)
        if S3EventObjectCopy.service_exception(response):
            raise dai_error.DaiS3CopyObjectError(s3_bucket_location)
        if self.remove_processed:
            destination_object_info = self._get_object_info(self.destination_bucket, destination_prefix)
            self._remove_processed_object(source_bucket=source_bucket_name, source_prefix=source_object,
                                          source_object_info=object_info,
                                          destination_object_info=destination_object_info)

    def _copy_using_managed_transfer(self,
                                     copy_source_object: Dict[str, any],
                                     destination_prefix: str,
                                     content_length: Optional[int],
                                     destination_tags: Dict[str, any]):
        """
        Uses client.copy to copy an object from one location to another. This copy is a so called managed transfer.

        client.copy docs:

                "This is a managed transfer which will perform a multipart copy in multiple threads if necessary."

        :param copy_source_object: Dict containing information about the source bucket and key
        :param destination_prefix: The destination prefix
        :param content_length: The size of the object
        :param destination_tags: Tags that should be set on the object in the request.
        :return:
        """
        s3_bucket_location = S3BucketLocation(copy_source_object.get("Bucket"),
                                              copy_source_object.get("Key"),
                                              self.destination_bucket,
                                              destination_prefix)

        if S3Utils.is_raw_bucket(self.destination_bucket):
            raise dai_error.DaiS3CopyObjectError(
                s3_bucket_location,
                message="Can't copy object due to destination bucket requiring "
                        "object lock which is not supported by this method!"
            )

        tagging = self._get_tagging_str(destination_tags)

        self.s3_client.copy(CopySource=copy_source_object,
                            Bucket=self.destination_bucket,
                            Key=destination_prefix,
                            ExtraArgs={
                                "Tagging": tagging,
                                "TaggingDirective": "REPLACE"
                            })
        # this would require a polling mechanism; there is no plan to have objects so large,
        # so this should be implemented when/if the need arises
        if self.remove_processed:
            if not content_length:
                self.logger.warning("Unable to determine content length, unable to remove "
                                    "{source_bucket_name}/{source_object} ")
            elif content_length is not None and content_length > 4.9e9:
                self.logger.warning("Removal of processed objects for large objects (>= 5Gb) not supported "
                                    "unable to remove {source_bucket_name}/{source_object} ")
            else:
                raise dai_error.DaiS3Error(f"Don't know how to remove processed: {copy_source_object}")

    def _copy_one_object(self, source_bucket_name: str, source_object: str, destination_tags: Dict[str, any] = None):
        """
        Copies one object to the destination bucket

        :param source_bucket_name: Name of the bucket
        :param source_object: Key of the object to be copied
        :return: Nothing
        :raises dai_error.DaiS3CopyObjectError if the copy_object operation fails
        """

        self.logger.debug(f"Processing {source_bucket_name}/{source_object} ")
        # if needed, unzip the file in memory then copy
        if self.unzip_file:
            destination_prefix_wo_filename = self._get_destination_prefix(source_object, exclude_filename=True)
            self._unzip_and_copy(source_bucket_name, source_object, destination_prefix_wo_filename)
        else:
            # copy the file without unzipping
            copy_source_object = {'Bucket': source_bucket_name, 'Key': source_object}
            destination_prefix = self._get_destination_prefix(source_object, exclude_filename=False)

            self.logger.debug(f"{source_bucket_name}/{source_object} -> {self.destination_bucket}/{destination_prefix}")

            object_info = self._get_object_info(source_bucket_name, source_object)
            if object_info is not None:
                content_length = S3EventObjectCopy.extract_field_from_dict(object_info, "Size")
                # use different methods depending on object size
                if not self.remove_processed or content_length is None or content_length > 4.9e9:
                    self._copy_using_managed_transfer(content_length=content_length,
                                                      copy_source_object=copy_source_object,
                                                      destination_prefix=destination_prefix,
                                                      destination_tags=destination_tags)
                else:
                    self._copy_using_unmanaged_transfer(copy_source_object=copy_source_object,
                                                        destination_prefix=destination_prefix,
                                                        object_info=object_info, source_bucket_name=source_bucket_name,
                                                        source_object=source_object, destination_tags=destination_tags)
            else:
                self.logger.warning(
                    f"The object {source_bucket_name}/{source_object} does not exist, perhaps it was already copied?")

        self.logger.debug(f"Finished processing {source_bucket_name}/{source_object} ")

    def copy_objects_s3_event(self, event: Dict[str, Any], destination_tags: Dict[str, any] = None) -> int:
        """
        Copy the object(s) that triggered an S3 event to a destination bucket.

        :param event: The event that triggered the function
        :param destination_tags: The tags that should be added to the object in the destination
        :return: the number of objects copied
        """
        num_records_copied = 0
        for record in event['Records']:
            source_bucket_name = record['s3']['bucket']['name']
            if source_bucket_name.strip() == self.destination_bucket:
                incorrect_inputs = {"destination_bucket_name": self.destination_bucket}
                raise dai_error.IncorrectInputValueError(
                    incorrect_inputs, "The destination bucket cannot be the same as the source bucket.")
            source_object = record['s3']['object']['key']
            try:
                self._copy_one_object(
                    source_bucket_name=source_bucket_name,
                    source_object=unquote_plus(source_object),
                    destination_tags=destination_tags
                )
                num_records_copied += 1
            except (BadZipFile, ClientError) as e:
                self.logger.exception(f"Caught exception: {e}")
                raise

        return num_records_copied
