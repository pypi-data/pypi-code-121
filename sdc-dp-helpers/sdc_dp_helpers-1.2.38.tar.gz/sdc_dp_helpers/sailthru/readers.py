"""
    CUSTOM READERS CLASSES
        - Class which manages reader tasks like auth, requests, pagination
"""
import os
import socket

from sailthru import SailthruClient

from sdc_dp_helpers.api_utilities.date_managers import date_range, date_handler
from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler
from sdc_dp_helpers.sailthru.config_magagers import get_config


class CustomSailThruReader:
    """
    Custom SailThru Reader
    """

    def __init__(self, config_filepath, creds_filepath):
        self.config = get_config(config_filepath)
        self.credentials = get_config(creds_filepath)

        self.sailthru_client = SailthruClient(
            api_key=self.credentials.get("api_key", None),
            secret=self.credentials.get("api_secret", None),
        )

    def _get_stat_templates(self):
        """
        Dynamically gathers all templates for 'send' stat.
        """
        response = self.sailthru_client.api_get(
            "template",
            {
                "start_date": date_handler(self.config["send"]["start_date"]),
                "end_date": date_handler(self.config["send"]["end_date"]),
            },
        )
        if response.is_ok():
            template_names = []
            template_data = response.get_body()
            for templates in template_data.get("templates"):
                template_names.append(templates.get("name"))

            return template_names

        raise EnvironmentError(
            f"Error: {response.get_error().get_error_code()}\n"
            f"Mesage: {response.get_error().get_message()}"
        )

    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 0)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
        backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    def _get_stat(self, data, action="stats"):
        response = self.sailthru_client.api_get(action=action, data=data)
        if response.is_ok():
            return response.get_body()
        elif not response.is_ok():
            error = response.get_error()
            message = "APIError:{}, Status Code:{}, Error Code:{}".format(
                error.get_message(),
                str(response.get_status_code()),
                str(error.get_error_code()),
            )

            if (
                str(response.get_status_code()) != "404"
                and str(error.get_error_code()) != "99"
            ):
                raise EnvironmentError(message)

            # If there is no data for something like a template,
            # just a warning is printed.
            print(f"Warning: No data in given instance.\n{message}.")
        else:
            return None

    @retry_handler(
        exceptions=(socket.timeout), total_tries=5, initial_wait=60, backoff_factor=5
    )
    def run_query(self):
        """
        Request various stats from Sailthru about primary list membership
        or campaign and triggered message activity.
        Endpoint URL: https://api.sailthru.com/stats
        Additional parameters are dependent on the stat value
        the type of stats you want to request:
            - list
            - blast
            - send
        """
        _data_set = []
        for action, data in self.config.items():
            _date_range_list = date_range(
                start_date=data["start_date"], end_date=data["end_date"]
            )

            if action == "blast":
                """
                Retrieve information about a particular campaign or aggregated information
                from all campaigns over a specified date range.
                """
                for _date in _date_range_list:
                    print(f"Gathering BLAST data for date: {_date}.")
                    stat_data = self._get_stat(
                        data={
                            "stat": "blast",
                            "start_date": _date,
                            "end_date": _date,
                        }
                    )

                    if stat_data is not None:
                        stat_data["date"] = _date
                        stat_data["stat"] = "blast"
                        _data_set.append(stat_data)

            elif action == "list":
                """
                Retrieve information about your subscriber counts on all lists or a particular
                list, as counted on a specified day’s snapshot, defaulting to the current day.
                """
                for _date in _date_range_list:
                    print(f"Gathering LIST data for date: {_date}.")
                    stat_data = self._get_stat(
                        data={
                            "stat": "list",
                            "date": _date,
                        }
                    )

                    if stat_data is not None:
                        stat_data["stat"] = "list"
                        _data_set.append(stat_data)

            elif action == "send":
                """
                Retrieve information about a particular triggered message or aggregated information
                from triggered messages from that template over a specified date range.
                """
                _template_names = self._get_stat_templates()
                print(f"Total templates: {len(_template_names)}.")
                for _date in _date_range_list:
                    for template_name in _template_names:
                        print(
                            f"Gathering SEND data at template: {template_name}. For date: {_date}."
                        )
                        stat_data = self._get_stat(
                            data={
                                "stat": "send",
                                "template": template_name,
                                "start_date": _date,
                                "end_date": _date,
                            }
                        )

                        if stat_data is not None:
                            stat_data["stat"] = "send"
                            stat_data["template"] = template_name
                            _data_set.append(stat_data)

            else:
                raise EnvironmentError(
                    f"Invalid action: {action} for stat endpoint. "
                    "Please use blast, list or send."
                )

        return _data_set
