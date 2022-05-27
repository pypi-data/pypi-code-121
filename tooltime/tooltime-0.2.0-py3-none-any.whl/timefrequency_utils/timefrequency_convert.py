from __future__ import annotations

from .. import spec
from .. import timelength_utils
from . import timefrequency_identify


def convert_timefrequency(
    timefrequency: spec.Timefrequency,
    to_representation: spec.TimefrequencyRepresentation,
    from_representation: spec.TimefrequencyRepresentation | None = None,
) -> spec.Timefrequency:
    """convert Timefrequency to a new representation

    ## Inputs
    - timefrequency: Timefrequency
    - to_representation: str of Timefrequency representation of input timefrequency
    - from_representation: str of target Timefrequency representation

    ## Returns
    - Timefrequency in specified representation
    """

    # determine current representation
    if from_representation is None:
        from_representation = (
            timefrequency_identify.detect_timefrequency_representation(
                timefrequency
            )
        )

    # check whether conversion is required
    if to_representation == from_representation:
        return timefrequency

    # perform conversion
    if to_representation == 'TimefrequencyFrequency':
        return timefrequency_to_frequency(
            timefrequency, from_representation=from_representation
        )
    elif to_representation == 'TimefrequencyCountPer':
        return timefrequency_to_count_per(
            timefrequency, from_representation=from_representation
        )
    elif to_representation == 'TimefrequencyInterval':
        return timefrequency_to_interval(
            timefrequency, from_representation=from_representation
        )
    else:
        raise Exception(
            'unknown timeperiod representation: ' + str(to_representation)
        )


def timefrequency_to_frequency(
    timefrequency: spec.Timefrequency,
    from_representation: spec.TimefrequencyRepresentation | None = None,
) -> spec.TimefrequencyFrequency:
    """convert Timefrequency to TimefrequencyFrequency representation

    ## Inputs
    - timefrequency: Timefrequency
    - from_representation: str representation name of input timefrequency

    ## Returns
    - TimefrequencyFrequency
    """

    if timefrequency_identify.is_timefrequency_frequency(timefrequency):
        return timefrequency
    elif timefrequency_identify.is_timefrequency_count_per(timefrequency):
        per_seconds = timelength_utils.timelength_to_seconds_precise(
            timefrequency['per']
        )
        return timefrequency['count'] / float(per_seconds)
    elif timefrequency_identify.is_timefrequency_interval(timefrequency):
        interval_seconds = timelength_utils.timelength_to_seconds_precise(
            timefrequency['interval']
        )
        return 1 / interval_seconds
    else:
        raise Exception('unknown Timefrequency representation')


def timefrequency_to_count_per(
    timefrequency: spec.Timefrequency,
    from_representation: spec.TimefrequencyRepresentation | None = None,
) -> spec.TimefrequencyCountPer:
    """convert Timefrequency to TimefrequencyCountPer representation

    ## Inputs
    - timefrequency: Timefrequency
    - from_representation: str representation name of input timefrequency

    ## Returns
    - TimefrequencyCountPer
    """

    if timefrequency_identify.is_timefrequency_frequency(timefrequency):
        return {'count': timefrequency, 'per': '1s'}
    elif timefrequency_identify.is_timefrequency_count_per(timefrequency):
        return timefrequency
    elif timefrequency_identify.is_timefrequency_interval(timefrequency):
        return {'count': 1, 'per': timefrequency['interval']}
    else:
        raise Exception('unknown Timefrequency representation')


def timefrequency_to_interval(
    timefrequency: spec.Timefrequency,
    from_representation: spec.TimefrequencyRepresentation | None = None,
) -> spec.TimefrequencyInterval:
    """convert Timefrequency to TimefrequencyInterval representation

    ## Inputs
    - timefrequency: Timefrequency
    - from_representation: str representation name of input timefrequency

    ## Returns
    - TimefrequencyInterval
    """

    if timefrequency_identify.is_timefrequency_frequency(timefrequency):
        return {'interval': 1 / float(timefrequency)}
    elif timefrequency_identify.is_timefrequency_count_per(timefrequency):
        per_seconds = timelength_utils.timelength_to_seconds(
            timefrequency['per']
        )
        return {'interval': per_seconds / timefrequency['count']}
    elif timefrequency_identify.is_timefrequency_interval(timefrequency):
        return timefrequency
    else:
        raise Exception('unknown Timefrequency representation')
