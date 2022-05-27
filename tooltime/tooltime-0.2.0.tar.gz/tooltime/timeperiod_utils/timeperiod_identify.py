from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard

from .. import spec
from .. import exceptions
from .. import timestamp_utils


def detect_timeperiod_representation(
    timeperiod: spec.Timeperiod,
) -> spec.TimeperiodRepresentation:
    """return str name of Timeperiod representation"""
    if is_timeperiod_map(timeperiod):
        return 'TimeperiodMap'
    elif is_timeperiod_pair(timeperiod):
        return 'TimeperiodPair'
    else:
        raise exceptions.RepresentationDetectionException(
            'could not detect timeperiod representation: ' + str(timeperiod)
        )


def is_timeperiod(timeperiod: typing.Any) -> TypeGuard[spec.Timeperiod]:
    """return bool of whether input is Timeperiod"""
    try:
        detect_timeperiod_representation(timeperiod)
        return True
    except Exception:
        return False


def is_timeperiod_map(
    timeperiod: typing.Any,
) -> TypeGuard[spec.TimeperiodMap]:
    """return bool of whether input is TimeperiodMap"""
    return (
        isinstance(timeperiod, dict)
        and len(timeperiod) == 2
        and 'start' in timeperiod
        and 'end' in timeperiod
        and timestamp_utils.is_timestamp(timeperiod['start'])
        and timestamp_utils.is_timestamp(timeperiod['end'])
    )


def is_timeperiod_pair(
    timeperiod: typing.Any,
) -> TypeGuard[spec.TimeperiodPair]:
    """return bool of whether input is TimeperiodPair"""
    return (
        isinstance(timeperiod, tuple)
        and len(timeperiod) == 2
        and timestamp_utils.is_timestamp(timeperiod[0])
        and timestamp_utils.is_timestamp(timeperiod[1])
    )

