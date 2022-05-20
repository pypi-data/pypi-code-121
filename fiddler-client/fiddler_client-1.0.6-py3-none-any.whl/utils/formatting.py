import re
import sys
from datetime import datetime

from .. import constants


def prettyprint_number(number, n_significant_figures=4):
    n_digits = len(f'{number:.0f}')
    return f'{round(number, n_significant_figures - n_digits):,}'


def _compute_hash(string):
    hash_value = 0
    if not string:
        return hash_value
    for c in string:
        hash_value = ((hash_value << 5) - hash_value) + ord(c)
        hash_value = hash_value & 0xFFFFFFFF  # Convert to 32bit integer
    return str(hash_value)


def sanitized_name(name):
    if name.isnumeric():
        name = f'_{name}'
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    if len(name) > 63:
        suffix = f'_{_compute_hash(name)}'
        name = f'{name[0: 63 - len(suffix)]}{suffix}'
    return name


def validate_sanitized_names(columns, sanitized_name_dict):
    if not columns:
        return
    if isinstance(columns, str):
        columns = [columns]
    for column in columns:
        sname = sanitized_name(column.name)
        if sname in sanitized_name_dict:
            other_name = sanitized_name_dict.get(sname)
            raise ValueError(
                f'Name conflict, {column.name} and {other_name} '
                f'both maps to {sname}'
            )
        else:
            sanitized_name_dict[sname] = column.name


def pad_timestamp(str_ts) -> str:
    """
    Attempts to return a padded timestamp of format '%Y-%m-%d %H:%M:%S.%f'.
    Will pad with 0's as necessary.
    """
    # 2021-01-01 00:00:00.000000
    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}', str_ts):
        ts = str_ts
    # 2021-01-01 00:00:00.0+
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+', str_ts):
        # Case of <6 floating point seconds
        ts = str_ts
        while not re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}', ts):
            ts = f'{ts}0'
    # 2021-01-01 00:00:00
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str_ts):
        # Case of no floating point seconds
        ts = f'{str_ts}.000000'
    # 2021-01-01
    elif re.match(r'\d{4}-\d{2}-\d{2}', str_ts):
        ts = f'{str_ts} 00:00:00.000000'
    # If it doesn't match any other format, then we just mark as a failure
    else:
        ts = str_ts

    return ts


def formatted_utcnow(milliseconds=None) -> str:
    """:return: UTC timestamp in '%Y-%m-%d %H:%M:%S.%f' format."""
    if milliseconds:
        if type(milliseconds) != int:
            raise ValueError(
                f'Timestamp has to be provided in milliseconds '
                f'as an integer. Provided timestamp was '
                f'{milliseconds} of {type(milliseconds)}'
            )
        return datetime.utcfromtimestamp(milliseconds / 1000.0).strftime(
            constants.TIMESTAMP_FORMAT
        )
    return datetime.utcnow().strftime(constants.TIMESTAMP_FORMAT)


def print_streamed_result(res: str):
    if res.startswith(constants.ONE_LINE_PRINT):
        print(f'\r{res[len(constants.ONE_LINE_PRINT):]}', end='')
        sys.stdout.flush()
    else:
        print(res)


def model_string_to_hostname(name):
    # Allow only a-z, 0-9, and _
    return re.sub(r'[^a-zA-Z0-9]', '-', name).lower()
