from __future__ import annotations

import typing

from .. import spec
from . import timeperiod_identify


@typing.overload
def convert_timeperiod(
    timeperiod: spec.Timeperiod,
    to_representation: typing.Literal['TimeperiodPair'],
    from_representation: typing.Optional[spec.TimeperiodRepresentation],
) -> spec.TimeperiodPair:
    ...


@typing.overload
def convert_timeperiod(
    timeperiod: spec.Timeperiod,
    to_representation: typing.Literal['TimeperiodMap'],
    from_representation: typing.Optional[spec.TimeperiodRepresentation],
) -> spec.TimeperiodMap:
    ...


def convert_timeperiod(
    timeperiod: spec.Timeperiod,
    to_representation: spec.TimeperiodRepresentation,
    from_representation: typing.Optional[spec.TimeperiodRepresentation] = None,
) -> spec.Timeperiod:
    """convert Timeperiod to a new representation

    ## Inputs
    - timeperiod: Timeperiod
    - to_representation: str of Timeperiod representation of input timeperiod
    - from_representation: str of target Timeperiod representation

    ## Returns
    - Timeperiod in specified representation
    """

    # determine current representation
    if from_representation is None:
        from_representation = (
            timeperiod_identify.detect_timeperiod_representation(timeperiod)
        )

    # check whether conversion is required
    if to_representation == from_representation:
        return timeperiod

    # perform conversion
    if to_representation == 'TimeperiodPair':
        return timeperiod_to_pair(
            timeperiod, from_representation=from_representation
        )
    elif to_representation == 'TimeperiodMap':
        return timeperiod_to_map(
            timeperiod, from_representation=from_representation
        )
    else:
        raise Exception(
            'unknown timeperiod representation: ' + str(to_representation)
        )


def timeperiod_to_pair(
    timeperiod: spec.Timeperiod,
    from_representation: spec.TimeperiodRepresentation = None,
) -> spec.TimeperiodPair:
    """convert Timeperiod to TimeperiodPair

    ## Inputs
    - timeperiod: Timeperiod
    - from_representation: str representation name of input timeperiod

    ## Returns
    - TimeperiodPair
    """

    if timeperiod_identify.is_timeperiod_map(timeperiod):
        return (timeperiod['start'], timeperiod['end'])
    elif timeperiod_identify.is_timeperiod_pair(timeperiod):
        return timeperiod
    else:
        from_representation = (
            timeperiod_identify.detect_timeperiod_representation(timeperiod)
        )
        raise Exception(
            'unknown Timeperiod representation: ' + str(from_representation)
        )


def timeperiod_to_map(
    timeperiod: spec.Timeperiod,
    from_representation: spec.TimeperiodRepresentation = None,
) -> spec.TimeperiodMap:
    """convert Timeperiod to TimeperiodMap

    ## Inputs
    - timeperiod: Timeperiod
    - from_representation: str representation name of input timeperiod

    ## Returns
    - TimeperiodMap
    """

    if timeperiod_identify.is_timeperiod_pair(timeperiod):
        start, end = timeperiod
        return {'start': start, 'end': end}
    elif timeperiod_identify.is_timeperiod_map(timeperiod):
        return timeperiod
    else:
        from_representation = (
            timeperiod_identify.detect_timeperiod_representation(timeperiod)
        )
        raise Exception(
            'unknown Timeperiod representation: ' + str(from_representation)
        )

