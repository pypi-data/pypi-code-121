from __future__ import annotations

import datetime
import typing

from .. import spec
from . import timestamp_identify


time_format = '%Y%m%d_%H%M%SZ'
precise_time_format = time_format[:-1] + '%f' + time_format[-1]


#
# # general conversion
#


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampSeconds'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampSeconds:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampSecondsPrecise'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampSecondsPrecise:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampLabel'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampLabel:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampISO'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampISO:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampISOPretty'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampISOPretty:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampDate'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampDate:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampYear'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampYear:
    ...


@typing.overload
def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: typing.Literal['TimestampDatetime'],
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.TimestampDatetime:
    ...


def convert_timestamp(
    timestamp: spec.Timestamp,
    to_representation: spec.TimestampRepresentation,
    from_representation: typing.Optional[spec.TimestampRepresentation] = None,
) -> spec.Timestamp:
    """convert timestamp to a new representation

    ## Inputs
    - timestamp: Timestamp
    - to_representation: str of Timestamp representation of input timestamp
    - from_representation: str of target Timestamp representation

    ## Returns
    - Timestamp in specified representation
    """

    # determine current representation
    if from_representation is None:
        from_representation = (
            timestamp_identify.detect_timestamp_representation(timestamp)
        )

    # check if representation is required
    if from_representation == to_representation:
        return timestamp

    # convert to seconds
    if timestamp_identify.is_timestamp_seconds(timestamp):
        timestamp_seconds: spec.TimestampSecondsRaw = timestamp
    elif timestamp_identify.is_timestamp_seconds_precise(timestamp):
        timestamp_seconds = timestamp
    elif timestamp_identify.is_timestamp_label(timestamp):
        timestamp_seconds = timestamp_label_to_seconds(timestamp)
    elif timestamp_identify.is_timestamp_iso(timestamp):
        timestamp_seconds = timestamp_iso_to_seconds(timestamp)
    elif timestamp_identify.is_timestamp_iso_pretty(timestamp):
        timestamp_seconds = timestamp_iso_pretty_to_seconds(timestamp)
    elif timestamp_identify.is_timestamp_date(timestamp):
        timestamp_seconds = timestamp_date_to_seconds(timestamp)
    elif timestamp_identify.is_timestamp_year(timestamp):
        timestamp_seconds = timestamp_year_to_seconds(timestamp)
    elif timestamp_identify.is_timestamp_datetime(timestamp):
        timestamp_seconds = timestamp_datetime_to_seconds(timestamp)
    else:
        raise Exception(
            'unknown timestamp representation: ' + str(from_representation)
        )

    # convert to target representation
    if to_representation == 'TimestampSeconds':
        return int(float(timestamp_seconds))
    elif to_representation == 'TimestampSecondsPrecise':
        return float(timestamp_seconds)
    elif to_representation == 'TimestampLabel':
        return timestamp_seconds_to_label(timestamp_seconds)
    elif to_representation == 'TimestampISO':
        return timestamp_seconds_to_iso(timestamp_seconds)
    elif to_representation == 'TimestampISOPretty':
        return timestamp_seconds_to_iso_pretty(timestamp_seconds)
    elif to_representation == 'TimestampDate':
        return timestamp_seconds_to_date(timestamp_seconds)[:10]
    elif to_representation == 'TimestampYear':
        return timestamp_seconds_to_year(timestamp_seconds)
    elif to_representation == 'TimestampDatetime':
        return timestamp_seconds_to_datetime(timestamp_seconds)
    else:
        raise Exception(
            'unknown timestamp representation: ' + str(to_representation)
        )


#
# # functions with target representation specified
#


def timestamp_to_seconds(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampSeconds:
    """convert timestamp to TimestampSeconds

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampSeconds timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampSeconds',
        from_representation=from_representation,
    )


def timestamp_to_seconds_precise(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampSecondsPrecise:
    """convert timestamp to TimestampSecondsPrecise

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampSecondsPrecise timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampSecondsPrecise',
        from_representation=from_representation,
    )


def timestamp_to_label(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampLabel:
    """convert timestamp to TimestampLabel

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampLabel timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampLabel',
        from_representation=from_representation,
    )


def timestamp_to_iso(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampISO:
    """convert timestamp to TimestampISO

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampISO timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampISO',
        from_representation=from_representation,
    )


def timestamp_to_iso_pretty(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampISOPretty:
    """convert timestamp to TimestampISOPretty

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampISOPretty timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampISOPretty',
        from_representation=from_representation,
    )


def timestamp_to_date(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampDate:
    """convert timestamp to TimestampDate

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampDate timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampDate',
        from_representation=from_representation,
    )


def timestamp_to_year(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampYear:
    """convert timestamp to TimestampYear

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampYear timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampYear',
        from_representation=from_representation,
    )


def timestamp_to_datetime(
    timestamp: spec.Timestamp,
    from_representation: spec.TimestampRepresentation = None,
) -> spec.TimestampDatetime:
    """convert timestamp to TimestampDatetime

    ## Inputs
    - timestamp: Timestamp
    - from_representation: str representation name of input timestamp

    ## Returns
    - TimestampDatetime timestamp
    """
    return convert_timestamp(
        timestamp,
        to_representation='TimestampDatetime',
        from_representation=from_representation,
    )


#
# # specific conversion functions, from seconds
#


def timestamp_seconds_to_label(
    timestamp_seconds: spec.TimestampSecondsRaw,
) -> spec.TimestampLabel:
    """convert seconds to TimestampLabel"""
    dt = datetime.datetime.fromtimestamp(
        float(timestamp_seconds), datetime.timezone.utc
    )
    human_timestamp = dt.strftime(time_format)
    return human_timestamp


def timestamp_seconds_to_iso(
    timestamp_seconds: spec.TimestampSecondsRaw,
) -> spec.TimestampISO:
    """convert seconds to TimestampISO"""
    dt = datetime.datetime.fromtimestamp(
        float(timestamp_seconds), datetime.timezone.utc
    )
    iso_format = "%Y-%m-%dT%H:%M:%SZ"
    iso = dt.strftime(iso_format)
    return iso


def timestamp_seconds_to_iso_pretty(
    timestamp_seconds: spec.TimestampSecondsRaw,
) -> spec.TimestampISOPretty:
    """convert seconds to TimestampISOPretty"""
    return timestamp_seconds_to_iso(timestamp_seconds).replace('T', ' ')


def timestamp_seconds_to_date(
    timestamp_seconds: spec.TimestampSecondsRaw,
) -> spec.TimestampDate:
    dt = timestamp_seconds_to_datetime(timestamp_seconds)
    return str(dt.year) + '-' + ('%.02d' % dt.month) + '-' + ('%.02d' % dt.day)


def timestamp_seconds_to_year(
    timestamp_seconds: spec.TimestampSecondsRaw,
) -> spec.TimestampDate:
    dt = timestamp_seconds_to_datetime(timestamp_seconds)
    return str(dt.year)


def timestamp_seconds_to_datetime(
    timestamp_seconds: spec.TimestampSecondsRaw,
) -> spec.TimestampDatetime:
    """convert seconds to TimestampDatetime"""
    return datetime.datetime.fromtimestamp(
        float(timestamp_seconds), datetime.timezone.utc
    )


#
# # specific conversion functions, to seconds
#


def timestamp_label_to_seconds(
    timestamp_label: spec.TimestampLabel,
) -> spec.TimestampSecondsRaw:
    """convert TimestampLabel to seconds"""

    timestamp = timestamp_label

    if timestamp_label[-1] != 'Z' or len(timestamp_label) != 16:
        raise Exception('timestamp label not in format ' + str(time_format))

    dt = datetime.datetime(
        year=int(timestamp[:4]),
        month=int(timestamp[4:6]),
        day=int(timestamp[6:8]),
        hour=int(timestamp[9:11]),
        minute=int(timestamp[11:13]),
        second=int(timestamp[13:15]),
        tzinfo=datetime.timezone.utc,
    )
    return dt.timestamp()


def timestamp_iso_to_seconds(
    timestamp_iso: spec.TimestampISO,
) -> spec.TimestampSecondsRaw:
    """convert TimestampISO to seconds"""

    if '.' in timestamp_iso:
        iso_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    else:
        iso_format = "%Y-%m-%dT%H:%M:%SZ"

    local_dt = datetime.datetime.strptime(timestamp_iso, iso_format)
    utc_dt = local_dt.replace(tzinfo=datetime.timezone.utc)
    seconds = utc_dt.timestamp()

    return seconds


def timestamp_iso_pretty_to_seconds(
    timestamp_iso_pretty: spec.TimestampISOPretty,
) -> spec.TimestampSecondsRaw:
    """convert TimestampISOPretty to seconds"""

    return timestamp_iso_to_seconds(timestamp_iso_pretty.replace(' ', 'T'))


def timestamp_date_to_seconds(
    timestamp_date: spec.TimestampDate,
) -> spec.TimestampSecondsRaw:

    import datetime

    year, month, day = timestamp_date.split('-')
    dt = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        tzinfo=datetime.timezone.utc,
    )
    return dt.timestamp()


def timestamp_year_to_seconds(
    timestamp_date: spec.TimestampYear,
) -> spec.TimestampSecondsRaw:

    import datetime

    dt = datetime.datetime(
        year=int(timestamp_date),
        month=1,
        day=1,
        tzinfo=datetime.timezone.utc,
    )
    return dt.timestamp()


def timestamp_datetime_to_seconds(
    timestamp_datetime: spec.TimestampDatetime,
) -> spec.TimestampSecondsRaw:
    """convert TimestampDatetime to seconds"""
    return timestamp_datetime.timestamp()


def timestamp_to_numerical(
    timestamp: spec.Timestamp,
) -> typing.Union[spec.TimestampSeconds, spec.TimestampSecondsPrecise]:
    if type(timestamp).__name__.startswith('int'):
        if isinstance(timestamp, typing.SupportsInt):
            return int(timestamp)
        else:
            raise Exception('bad type: ' + str(type(timestamp)))
    else:
        return timestamp_to_seconds_precise(timestamp)
