import json
import os
import time

import requests as req
from dotenv import load_dotenv

from qapi_sdk.logs import get_logger

load_dotenv()
ENV = os.getenv

logger = get_logger(os.path.basename(__file__))


class Query:
    """
    Query class for pushing data to QAPI
    :param feed_id:str: Specify the feed to which we want to push the query
    :param query_id:str: Identify the query in the qapi
    :param sql:str: Pass the sql query to be executed
    """

    def __init__(self, feed_id: str, query_id: str):
        """
        :param self: Refer to the object itself
        :param feed_id:str: Store the id of the feed that is being used
        :param query_id:str: Store the query id of the feed
        :return: The object that is created when the class is called
        :doc-author: Me
        """
        self.feed_id = feed_id
        self.query_id = query_id

    def push_query(self, sql: str) -> str:
        """
        The push_query function is used to push a query to the QAPI.
        The function takes in an SQL string and returns a status code from the request.
        :param self: Access variables that belongs to the class
        :param sql:str: Pass in the sql query that you want to run
        :return: The status code and message of the request
        :doc-author: Me
        """
        logger.info(f"Pushing QUERY: [{self.query_id}] to FEED: [{self.feed_id}]")
        try:
            payload = {
                "feed_id": self.feed_id,
                "query_id": self.query_id,
                "query": {
                    "sql": sql,
                },
                "success_callback": f"mailto:{ENV('EMAIL')}?subject=QUERY_SUCCESS",
                "error_callback": f"mailto:{ENV('EMAIL')}?subject=QUERY_FAILED",
                "format": {
                    "type": "csv",
                    "separator": ",",
                    "string_delimiter": "\"",
                },
                "has_header": True,
                "returns_data": True,
                "request_metadata": self.query_id,
            }
            response = req.post(f"{ENV('QAPI_URL')}/query/sql", json=payload, timeout=60)
            logger.info(json.dumps(payload, indent=4))
            logger.info(f"FROM QUERY PUSH: {response.status_code}: {response.json()['message']}")
        except req.exceptions.RequestException as e:
            logger.error(e)
            return f"Error: Unexpected response {e}"

    def query_status(self, max_tries=5) -> bool:
        """
        The query_status function is used to check the status of a query.
        :param self: Access variables that belongs to the class
        :param max_tries: Define the number of times to try and query the status of a query
        :return: A boolean value
        :doc-author: Me
        """
        success_codes = (200, 201)
        success_statuses = ("RUNNING", "unknown", "QUEUED")
        tries_404 = 0
        while tries_404 < max_tries:
            try:
                response = req.get(f"{ENV('QAPI_URL')}/query/status?query_id={self.query_id}&feed_id={self.feed_id}",
                                   timeout=60)
                logger.info(f"QUERY STATUS: {response.status_code}")
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

    def delete_query(self) -> str:
        """
        The delete_query function deletes a query from the QAPI.
        :param self: Access the attributes and methods of the class in python
        :return: A string
        :doc-author: Me
        """
        """"""
        logger.info(f"DELETE QUERY: [{self.query_id}] FROM FEED: [{self.feed_id}]")
        try:
            payload = {
                "feed_id": self.feed_id,
                "query_id": self.query_id,
            }
            response = req.delete(f"{ENV('QAPI_URL')}/query/sql", json=payload, timeout=60)
            logger.info(json.dumps(payload, indent=4))
            logger.info(response.json())
            if response.status_code // 100 != 2:
                return f"Error: Unexpected response {response}"
        except req.exceptions.RequestException as e:
            logger.error(e)
