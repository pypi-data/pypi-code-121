import json
import os
import time
import csv
import boto3
import botocore.exceptions
from smart_open import open

import requests as req
from dotenv import load_dotenv

from qapi_sdk.logs import get_logger

load_dotenv()
ENV = os.getenv

logger = get_logger(os.path.basename(__file__))

s3 = boto3.resource(
    service_name='s3',
    aws_access_key_id=ENV('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=ENV('AWS_SECRET_ACCESS_KEY'),
    region_name=ENV('AWS_DEFAULT_REGION'),
)


class Feed:
    """
        Push class for pushing data to QAPI
        :param feed_id:str: Specify the feed that will be pushed
        :param push_id:str: Uniquely identify the push
        """

    def __init__(self, feed_id: str, push_id: str):
        self.feed_id = feed_id
        self.push_id = push_id

    def push_feed(self, pull_path_bucket: str, pull_path_key: str, columns: list, separator: str) -> str:
        """
        The push_feed function pushes a feed to the QAPI.
        :param pull_path_bucket:str: Specify the bucket where the file is located
        :param pull_path_key:str: Specify the key of the file in s3 that you want to push
        :param columns:list: Specify the columns that will be in the feed
        :param separator:str: Specify the character used to separate fields in a csv file
        :return: The status code and message from the api
        :doc-author: TheBridgeDan
        """
        logger.info('PUSHING FEED...')
        try:
            payload = {
                "feed_id": self.feed_id,
                "push_id": self.push_id,
                "success_callback": f"mailto:{ENV('EMAIL')}?subject=PUSH_SUCCESS",
                "error_callback": f"mailto:{ENV('EMAIL')}?subject=PUSH_FAILED",
                "format": {
                    "type": "csv",
                    "parameters": {
                        "separator": separator,
                        "string_delimiter": "\"",
                        "has_header": True,
                    }
                },
                "columns": columns,
                "pull_paths": [
                    {
                        "bucket": pull_path_bucket,
                        "key": pull_path_key
                    }
                ],
                "request_metadata": f"FeedID: {self.feed_id}, PushID: {self.push_id}"

            }
            response = req.post(f"{ENV('QAPI_URL')}/feed/push/s3", json=payload, timeout=60)
            logger.info(json.dumps(payload, indent=4))
            logger.info(f"FROM FEED PUSH: {response.status_code}: {response.json()['message']}")
        except req.exceptions.RequestException as e:
            logger.error(e)
            return f"Error: Unexpected response {e}"

    def push_status(self, max_tries=5) -> bool:
        """
        The query_status function is used to check the status of a query.
        :param self: Access variables that belongs to the class
        :param max_tries: Define the number of times to try and query the status of a query
        :return: A boolean value
        :doc-author: TheBridgeDan
        """
        success_codes = (200, 201)
        success_statuses = ("processing", "received")
        tries_404 = 0
        while tries_404 < max_tries:
            try:
                response = req.get(f"{ENV('QAPI_URL')}/feed/push/status?feed_id={self.feed_id}&push_id={self.push_id}",
                                   timeout=60)
                logger.info(f"PUSH STATUS: {response.status_code}")
                if response.status_code not in success_codes:
                    tries_404 += 1
                    time.sleep(5)
                    logger.info("Try again...")
                    continue
                if response.json()['status'] in success_statuses:
                    logger.info(response.json()['status'])
                    return True
                else:
                    logger.info(response.json()['status'])
                    logger.info(response.json())
                    return False
            except req.exceptions.RequestException as e:
                logger.error(e)
                return False

    def delete_feed(self) -> str:
        """
        The delete_feed function deletes a feed from the QAPI.
        :param self: Access the attributes and methods of the class in python
        :return: A string
        :doc-author: TheBridgeDan
        """
        logger.info(f"DELETING FEED: [{self.feed_id}]")
        try:
            payload = {
                "feed_id": self.feed_id,
                "success_callback": f"mailto:{ENV('EMAIL')}?subject=DELETE_FEED_SUCCESS",
                "error_callback": f"mailto:{ENV('EMAIL')}?subject=DELETE_FEED_FAILED",
                "request_metadata": self.feed_id
            }
            response = req.delete(f"{ENV('QAPI_URL')}/feed/s3", json=payload, timeout=60)
            logger.info(json.dumps(payload, indent=4))
            logger.info(response.json())
            if response.status_code // 100 != 2:
                return f"Error: Unexpected response {response}"
        except req.exceptions.RequestException as e:
            logger.error(e)

    def delete_push(self) -> str:
        """
        The delete_feed function deletes a feed from the QAPI.
        :param self: Access the attributes and methods of the class in python
        :return: A string
        :doc-author: TheBridgeDan
        """
        logger.info(f"DELETING PUSH ID: [{self.push_id}] FROM FEED: [{self.feed_id}]")
        try:
            payload = {
                "feed_id": self.feed_id,
                "push_id": self.push_id,
                "success_callback": f"mailto:{ENV('EMAIL')}?subject=DELETE_PUSH_SUCCESS",
                "error_callback": f"mailto:{ENV('EMAIL')}?subject=DELETE_PUSH_FAILED"
            }
            response = req.delete(f"{ENV('QAPI_URL')}/feed/push/s3", json=payload, timeout=60)
            logger.info(json.dumps(payload, indent=4))
            logger.info(response.json())
            if response.status_code // 100 != 2:
                return f"Error: Unexpected response {response}"
        except req.exceptions.RequestException as e:
            logger.error(e)

    @staticmethod
    def read_columns(data_bucket: str, data_key_dir: str, delimiter: str) -> list:
        """
        The read_columns function reads the columns from a csv file and returns a list of dictionaries with column
        name and type.
        :param data_bucket:str: Specify the bucket where the data is located
        :param data_key_dir:str: Tell the function which folder to look in for csv files
        :param delimiter:str: Specify the delimiter used in the csv file
        :return: A list of dictionaries with the name and type of each column
        :doc-author: TheBridgeDan
        """
        try:
            for file in s3.Bucket(data_bucket).objects.filter(Prefix=data_key_dir):
                if file.key.endswith(".csv") or file.key.endswith(".txt") and file.key[-1]:
                    with open(f"s3://{data_bucket}/{file.key}", "r") as f:
                        reader = csv.DictReader(f, delimiter=delimiter)
                        return [{"name": column, "type": "string"} for column in reader.fieldnames]
        except botocore.exceptions.ClientError as e:
            logger.error(e)
