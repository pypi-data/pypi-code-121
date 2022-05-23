import logging
import datetime as dt
import time
from time import strftime

import coloredlogs
from dateutil import parser

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


def format_date(date):
    if date is None or date == "":
        return ""
    if type(date) is int:
        date = dt.datetime.fromtimestamp(date / 1e3)
        return date.strftime("%m/%d/%Y, %H:%M:%S")
    if len(date) > 0:
        # Convert and print date time in local timezone
        return parser.parse(date).astimezone().strftime("%m/%d/%y %H:%M")

    logger.warning(f"Invalid date found - [{date}]")
    return ""


def format_time(time_delta_in_seconds):
    if time_delta_in_seconds is None:
        return ""

    if type(time_delta_in_seconds) is str:
        if len(time_delta_in_seconds) == 0:
            return ""
        try:
            time_delta_in_seconds = int(time_delta_in_seconds)
        except ValueError as _:
            try:
                from tzlocal import get_localzone  # $ pip install tzlocal

                local_tz = get_localzone()
                date_time = dt.datetime.strptime(
                    time_delta_in_seconds, "%H:%M:%S.%f"
                ).replace(tzinfo=local_tz)
                time_delta_in_seconds = date_time.timestamp()
                time_delta_in_seconds = strftime(
                    "%Hh:%Mm:%Ss", time.localtime(time_delta_in_seconds)
                )
                return time_delta_in_seconds
            except ValueError as _:
                return time_delta_in_seconds

    if type(time_delta_in_seconds) is float:
        time_delta_in_seconds = int(time_delta_in_seconds)

    time_delta_in_seconds = strftime("%Hh:%Mm:%Ss", time.gmtime(time_delta_in_seconds))
    return time_delta_in_seconds


def transform_date():
    return lambda x: format_date(x)
