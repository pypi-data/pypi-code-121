import uuid
from datetime import datetime
from time import sleep
from typing import Union

from dateutil import parser
from dateutil.parser import ParserError
from pytz import timezone

from .general_runtime_vars import env_vars


def generate_guid():
    return str(uuid.uuid1())


def parse_headers(msg_header):
    """
    Converts headers to a dict
    :param msg_header: A message .headers() (confluent) or .headers (faust) instance
    :return: a decoded dict version of the headers
    """
    if msg_header:
        if not isinstance(msg_header, dict):
            msg_header = dict(msg_header)
            return {key: value.decode() for key, value in msg_header.items()}
        return msg_header
    return {}


def log_and_raise_error(metrics_manager, error):
    """
    Since the metric manager pushing is a separate thread, ensure an exception gets sent to prometheus
    """
    metrics_manager.inc_message_errors(error)
    sleep(int(env_vars()['NU_METRICS_PUSH_RATE']) * 2 + 1)
    raise


def universal_datetime_converter(incoming_datetime: Union[str, datetime], incoming_timezone: timezone = timezone("Etc/UTC")) -> str:
    """
    Converts datetime values of all kinds into a normalized format
    Assumes midnight if datetime does not include time
    """
    universal_format = '%Y-%m-%dT%H:%M:%SZ'

    try:
        datetime_to_convert = parser.parse(str(incoming_datetime))
    except (ParserError, OverflowError):
        try:
            return datetime.utcfromtimestamp(int(incoming_datetime)).strftime(universal_format)
        except Exception:
            return ""

    if datetime_to_convert.tzinfo is None or datetime_to_convert.tzinfo.utcoffset(datetime_to_convert) is None:
        datetime_to_convert = incoming_timezone.normalize(incoming_timezone.localize(datetime_to_convert))

    datetime_to_convert = datetime_to_convert.astimezone(timezone("Etc/UTC"))
    converted_datetime = datetime_to_convert.strftime(universal_format)
    return converted_datetime
