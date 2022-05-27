from __future__ import annotations

import datetime
import typing

from .. import spec
from .. import timestamp_utils
from .. import timelength_utils
from . import timeperiod_identify


def create_timeperiod(
    start: spec.Timestamp = None,
    end: spec.Timestamp = None,
    length: spec.Timelength = None,
    to_representation: spec.TimeperiodRepresentation = None,
) -> spec.Timeperiod:
    """create Timeperiod

    ## Inputs
    - start: Timestamp
    - end: Timestamp
    - length: Timelength
    - to_reprsentation: str name of Timeperiod representation

    ## Returns
    - Timeperiod with specified representation
    """

    if to_representation is None:
        to_representation = 'TimeperiodMap'

    if to_representation == 'TimeperiodMap':
        return create_timeperiod_map(start=start, end=end, length=length)
    elif to_representation == 'TimeperiodPair':
        return create_timeperiod_pair(start=start, end=end, length=length)
    else:
        raise Exception(
            'unknown timeperiod representation: ' + str(to_representation)
        )


def create_timeperiod_pair(
    start: spec.Timestamp = None,
    end: spec.Timestamp = None,
    length: spec.Timelength = None,
) -> spec.TimeperiodPair:
    """create Timeperiod with representation TimeperiodPair

    ## Inputs
    - start: Timestamp
    - end: Timestamp
    - length: Timelength

    ## Returns
    - TimeperiodPair
    """
    start, end = compute_start_end(start=start, end=end, length=length)
    return (start, end)


def create_timeperiod_map(
    start: spec.Timestamp = None,
    end: spec.Timestamp = None,
    length: spec.Timelength = None,
) -> spec.TimeperiodMap:
    """create Timeperiod with representation TimeperiodMap

    ## Inputs
    - start: Timestamp
    - end: Timestamp
    - length: Timelength

    ## Returns
    - TimeperiodMap
    """
    start, end = compute_start_end(start=start, end=end, length=length)
    return {'start': start, 'end': end}


def compute_start_end(
    start: spec.Timestamp = None,
    end: spec.Timestamp = None,
    length: spec.Timelength = None,
) -> tuple[typing.Union[int, float], typing.Union[int, float]]:
    """return start and end given two of start, end, and length

    ## Inputs
    - start: Timestamp
    - end: Timestamp
    - length: Timelength

    ## Returns
    - TimeperiodPair
    """

    # convert inputs to seconds
    if start is not None:
        start = timestamp_utils.timestamp_to_seconds(start)
    if end is not None:
        end = timestamp_utils.timestamp_to_seconds(end)
    if length is None:
        length_seconds: typing.Union[int, float, None] = None
    elif isinstance(length, int):
        length_seconds = length
    elif isinstance(length, datetime.timedelta) or isinstance(length, str):
        length_seconds = timelength_utils.timelength_to_seconds_precise(length)

    # compute unknown bounds
    if end is not None and length_seconds is not None:
        start = end - length_seconds
    elif start is not None and length_seconds is not None:
        end = start + length_seconds
    elif start is not None and end is not None:
        pass
    else:
        raise Exception('must specify exactly 2 inputs')

    if type(start).__name__.startswith('int'):
        start = int(start)
    else:
        start = float(start)
    if type(end).__name__.startswith('int'):
        end = int(end)
    else:
        end = float(end)

    return (start, end)


def compute_timeperiod_start_end(
    timeperiod: spec.Timeperiod,
) -> tuple[typing.Union[int, float], typing.Union[int, float]]:
    """compute start and end seconds of a timeperiod"""

    if timeperiod_identify.is_timeperiod_pair(timeperiod):
        start, end = timeperiod
    elif timeperiod_identify.is_timeperiod_map(timeperiod):
        start = timeperiod['start']
        end = timeperiod['end']
    else:
        representation = timeperiod_identify.detect_timeperiod_representation(
            timeperiod
        )
        raise Exception(
            'unknown timeperiod representation: ' + str(representation)
        )

    start_numerical = timestamp_utils.timestamp_to_numerical(start)
    end_numerical = timestamp_utils.timestamp_to_numerical(end)

    return (start_numerical, end_numerical)

