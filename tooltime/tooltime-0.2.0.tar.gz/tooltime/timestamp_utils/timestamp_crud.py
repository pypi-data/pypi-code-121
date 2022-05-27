from __future__ import annotations

import time
import typing

from .. import spec
from . import timestamp_convert


def create_timestamp(
    seconds: typing.SupportsFloat = None,
    representation: spec.TimestampRepresentation = 'TimestampSeconds',
) -> spec.Timestamp:
    """create Timestamp

    ## Inputs
    - seconds: int or float utc seconds
    - representation: str name of Timestamp representation

    ## Returns
    - Timestamp with specified representation
    """
    if representation == 'TimestampSeconds':
        return create_timestamp_seconds(seconds=seconds)
    elif representation == 'TimestampSecondsPrecise':
        return create_timestamp_seconds_precise(seconds=seconds)
    elif representation == 'TimestampLabel':
        return create_timestamp_label(seconds=seconds)
    elif representation == 'TimestampISO':
        return create_timestamp_iso(seconds=seconds)
    elif representation == 'TimestampDatetime':
        return create_timestamp_datetime(seconds=seconds)
    else:
        raise Exception('unknown representation: ' + str(representation))


def create_timestamp_seconds(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampSeconds:
    """create Timestamp with representation TimestampSeconds"""
    if seconds is None:
        seconds = time.time()
    return int(float(seconds))


def create_timestamp_seconds_precise(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampSecondsPrecise:
    """create Timestamp with representation TimestampSecondsPrecise"""
    if seconds is None:
        seconds = time.time()
    return float(seconds)


def create_timestamp_label(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampLabel:
    """create Timestamp with representation TimestampLabel"""
    if seconds is None:
        seconds = time.time()
    return timestamp_convert.timestamp_seconds_to_label(seconds)


def create_timestamp_iso(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampISO:
    """create Timestamp with representation TimestampISO"""
    if seconds is None:
        seconds = time.time()
    return timestamp_convert.timestamp_seconds_to_iso(seconds)


def create_timestamp_iso_pretty(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampISOPretty:
    """create Timestamp with representation TimestampISOPretty"""
    return create_timestamp_iso(seconds).replace('T', ' ')


def create_timestamp_date(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampDate:
    """create Timestamp with representation TimestampDate

    does not round to nearest date, takes floor of seconds to previous date
    """
    import datetime

    if seconds is None:
        dt = datetime.datetime.now(tz=datetime.timezone.utc)
    else:
        dt = datetime.datetime.fromtimestamp(
            float(seconds), tz=datetime.timezone.utc
        )

    year = dt.year
    month = dt.month
    day = dt.day
    return str(year) + '-' + ('%.02d' % month) + '-' + ('%.02d' % day)


def create_timestamp_year(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampYear:
    """create Timestamp with representation TimestampDate

    does not round to nearest year, takes floor of seconds to previous year
    """
    import datetime

    if seconds is None:
        dt = datetime.datetime.now(tz=datetime.timezone.utc)
    else:
        dt = datetime.datetime.fromtimestamp(
            float(seconds), tz=datetime.timezone.utc
        )

    return str(dt.year)


def create_timestamp_datetime(
    seconds: typing.SupportsFloat = None,
) -> spec.TimestampDatetime:
    """create Timestamp with representation TimestampDatetime"""
    if seconds is None:
        seconds = time.time()
    return timestamp_convert.timestamp_seconds_to_datetime(seconds)
