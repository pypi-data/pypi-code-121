"""Useful functions for s3 buckets"""
import re
from typing import Dict, List

import botocore.client
import loguru

from dai_python_commons import dai_error


class S3Utils:
    """
    Class provides functions to modify s3 buckets
    """
    RAW_BUCKET_PATTERN = re.compile(r'se-sl-tf-dai-[^-]*-data-raw')

    @staticmethod
    def delete_objects_by_prefix(boto_s3_client: botocore.client,
                                 bucket_name: str,
                                 prefix: str,
                                 logger: loguru.logger) -> int:
        """
        Deletes all objects with given prefix from a bucket

        :param boto_s3_client: S3 client to be used
        :param bucket_name: Name of the bucket
        :param prefix: Prefix of objects that should be removed
        :param logger: The logger
        :return: Number of objects deleted
        """
        logger.info(f"Deleting objects with prefix {prefix} from bucket {bucket_name}")

        paginator = boto_s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        # gather all objects to be deleted
        to_delete = []
        for item in page_iterator.search('Contents'):
            if not item:
                break
            to_delete.append(dict(Key=item['Key']))

        # delete the objects
        return S3Utils.delete_objects(boto_s3_client=boto_s3_client,
                                      bucket_name=bucket_name, to_delete=to_delete, logger=logger)

    @staticmethod
    def delete_objects(boto_s3_client: botocore.client,
                       bucket_name: str,
                       to_delete: List[Dict[str, str]],
                       logger: loguru.logger) -> int:
        """
        Deletes the specified objects in `to_delete` and returns the number of deleted objects.

        `to_delete` should be in the following format:

            [
                {
                    'Key': 'prefix'
                }
            ]

        :param boto_s3_client: S3 client to be used
        :param bucket_name: Name of the bucket
        :param to_delete: list of objects to delete
        :param logger: The logger
        :return: Number of objects deleted
        """

        start_index = 0
        while start_index < len(to_delete):
            end_index = min(len(to_delete), start_index + 1000)
            batch_to_delete = {"Objects": to_delete[start_index: end_index]}
            logger.debug(f"Deleting {batch_to_delete}")
            response = boto_s3_client.delete_objects(Bucket=bucket_name, Delete=batch_to_delete)

            # If something went wrong raise an error
            if 'Errors' in response and len(response["Errors"]) > 0:
                raise dai_error.DaiS3DeleteObjectError(s3_bucket=bucket_name, error_infos=response["Errors"])

            start_index = end_index

        logger.info(f"Number of objects deleted: {len(to_delete)}")

        return len(to_delete)

    @staticmethod
    def file_paths_in_prefix(boto_s3_client: botocore.client,
                             bucket_name: str,
                             prefix: str,
                             logger: loguru.logger) -> List[Dict[str, str]]:
        """
        Returns a list of dicts representing file paths in the format:

            [
                {
                    'Key': 'prefix'
                }
            ]

        :param boto_s3_client: S3 client to be used
        :param bucket_name: Name of the bucket
        :param prefix: Prefix where to list files
        :param logger: The logger
        :return: A list of file path dicts
        """
        paginator = boto_s3_client.get_paginator('list_objects_v2')
        prefix = prefix if prefix.endswith('/') else f'{prefix}/'
        file_paths = []
        for item in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/').search('Contents'):
            if item:
                file_paths.append({
                    'Key': item['Key']
                })

        logger.debug(f'In "{bucket_name}/{prefix}" found: {file_paths}')

        return file_paths

    @staticmethod
    def is_raw_bucket(bucket_name: str) -> bool:
        """Checks that bucket_name matches RAW_BUCKET_PATTERN regex"""
        return S3Utils.RAW_BUCKET_PATTERN.match(bucket_name) is not None
