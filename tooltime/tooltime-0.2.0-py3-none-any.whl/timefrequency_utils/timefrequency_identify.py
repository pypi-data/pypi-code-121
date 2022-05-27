from __future__ import annotations

import typing
from typing_extensions import TypeGuard

from .. import exceptions
from .. import spec
from .. import timelength_utils


def detect_timefrequency_representation(
    timefrequency: typing.Any,
) -> spec.TimefrequencyRepresentation:
    """return str name of Timefrequency representation"""
    if is_timefrequency_frequency(timefrequency):
        return 'TimefrequencyFrequency'
    elif is_timefrequency_count_per(timefrequency):
        return 'TimefrequencyCountPer'
    elif is_timefrequency_interval(timefrequency):
        return 'TimefrequencyInterval'
    else:
        raise exceptions.RepresentationDetectionException(
            'could not detect Timefrequency representation: '
            + str(timefrequency)
        )


def is_timefrequency(
    timefrequency: typing.Any,
) -> TypeGuard[spec.Timefrequency]:
    """return bool of whether input is Timefrequency"""
    try:
        detect_timefrequency_representation(timefrequency)
        return True
    except exceptions.RepresentationDetectionException:
        return False


def is_timefrequency_frequency(
    timefrequency: typing.Any,
) -> TypeGuard[spec.TimefrequencyFrequency]:
    """return bool of whether input is TimefrequencyFrequency"""
    return isinstance(timefrequency, (int, float))


def is_timefrequency_count_per(
    timefrequency: typing.Any,
) -> TypeGuard[spec.TimefrequencyCountPer]:
    """return bool of whether input is TimefrequencyCountPer"""
    return (
        isinstance(timefrequency, dict)
        and len(timefrequency) == 2
        and 'count' in timefrequency
        and 'per' in timefrequency
        and isinstance(timefrequency['count'], (int, float))
        and timelength_utils.is_timelength(timefrequency['per'])
    )


def is_timefrequency_interval(
    timefrequency: typing.Any,
) -> TypeGuard[spec.TimefrequencyInterval]:
    """return bool of whether input is TimefrequencyInterval"""
    return (
        isinstance(timefrequency, dict)
        and len(timefrequency) == 1
        and 'interval' in timefrequency
        and timelength_utils.is_timelength(timefrequency['interval'])
    )
