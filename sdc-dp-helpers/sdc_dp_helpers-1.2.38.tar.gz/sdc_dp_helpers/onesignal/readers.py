# pylint: disable=no-self-use
import json
import time
from datetime import datetime
from urllib.error import URLError

import pandas as pd
import requests
from dateutil import parser

from sdc_dp_helpers.api_utilities.date_managers import date_handler
from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import retry_handler, request_handler


class CustomOneSignalReader:
    def __init__(self, creds_file, config_file, **kwargs):
        self._creds = load_file(creds_file, "yml")
        self._config = load_file(config_file, "yml")

        self._header = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {self._creds.get('api_key')}",
            "User-Agent": "Mozilla/5.0",
        }

        self._request_session = requests.Session()
        self.offset, self.data_set = 0, []

        self._csv_wait_time = kwargs.get("csv_wait_time", 60)
        self._csv_get_attempts = kwargs.get("csv_get_attempts", 5)

    def _generate_url(self, endpoint: str):
        """
        Generate url string for authentication from given endpoints.
        :param endpoint: view_notification or csv_export
        :return: Url string.
        """
        _app_id = self._creds.get("app_id")
        if endpoint == "view_notifications":
            return f"https://onesignal.com/api/v1/notifications?app_id={_app_id}"
        if endpoint == "csv_export":
            return f"https://onesignal.com/api/v1/players/csv_export?app_id={_app_id}"

        raise ValueError(
            f"Given endpoint: {endpoint} is not supported. "
            f"Try csv_export or view_notifications."
        )

    @request_handler(wait=0.5, backoff_factor=0.5)
    def _view_notification_query_handler(self, limit: int, offset: int):
        """
        Handles the view notification request attempt.
        """
        url = self._generate_url(endpoint="view_notifications")
        return requests.get(
            url=url,
            headers=self._header,
            params={"limit": limit, "total_count": "true", "offset": offset},
        )

    @request_handler(wait=1, backoff_factor=0.5)
    def _csv_export_query_handler(self):
        """
        Handles the csv export request attempt.
        """
        url = self._generate_url(endpoint="csv_export")
        return requests.post(url=url, headers=self._header)

    def _get_csv_export_handler(self, response):
        """
        Attempts to gather the data from the csv url, and waits while
        it is being generated.
        :param response: Onesignal response object.
        """
        csv_url = response.get("csv_file_url", None)
        if csv_url is not None:
            attempts = 1
            while True:
                try:
                    print(f"Attempting to gather data from url: {csv_url}.")
                    data_frame: pd.DataFrame = pd.read_csv(csv_url)
                    self.data_set = data_frame.to_dict(orient="records")

                    # create a usable field to write to s3
                    # also handle timestamps that have milliseconds, it's not
                    # always there, so we need to handle both
                    for row in self.data_set:
                        try:
                            row["created_at_date"] = str(
                                datetime.strptime(
                                    row["created_at"], "%Y-%m-%d %H:%M:%S"
                                ).date()
                            ).replace("-", "")
                        except ValueError:
                            row["created_at_date"] = str(
                                datetime.strptime(
                                    row["created_at"], "%Y-%m-%d %H:%M:%S.%f"
                                ).date()
                            ).replace("-", "")

                    print("Data gathered...")
                    return self.data_set

                except URLError:
                    print(
                        f"CSV file not generated, waiting for {self._csv_wait_time} seconds. "
                        f"Attempt {attempts}/{self._csv_get_attempts}."
                    )
                    time.sleep(self._csv_wait_time)
                    if attempts >= self._csv_get_attempts:
                        raise ConnectionError(
                            f"CSV file failed to generate after {attempts} attempts. "
                            "Contact Onesignal for help."
                        )
                    attempts += 1
        else:
            raise ConnectionError(response)

    def run_query(self):
        """
        Generate a compressed CSV export of all of your current user data.
        This method can be used to generate a compressed CSV export of all of your current user data.
        View the details of multiple notifications.
        :return: The response dataset.
        """
        _endpoint = self._config.get("endpoint")
        _limit = self._config.get("limit", 50)
        print(f"Gathering data for {_endpoint}.")

        if _endpoint == "view_notifications":
            # gather data per offset given the set of limits
            initial_response = self._view_notification_query_handler(
                limit=_limit, offset=0
            ).json()
            _total_records = int(initial_response.get("total_count"))

            for offset in range(0, _total_records, _limit):
                print(f"At offset {offset} of {_total_records}.")
                response = self._view_notification_query_handler(
                    limit=_limit, offset=offset
                ).json()
                for notification in response.get("notifications"):
                    self.data_set.append(notification)

            return self.data_set

        if _endpoint == "csv_export":
            # if connection is good, try to get the csv file from the Onesignal
            # Athena wrapper, it could take time to generate, so wait for it.
            response = self._csv_export_query_handler().json()
            self._get_csv_export_handler(response=response)
            return self.data_set

        raise ValueError(
            f"Given endpoint: {_endpoint} is not supported. "
            f"Try csv_export or view_notifications."
        )
