from __future__ import annotations

from .. import spec
from .. import timelength_utils


def create_timefrequency(
    frequency: int | float | None = None,
    count: int | float | None = None,
    per: spec.Timelength | None = None,
    interval: spec.Timelength | None = None,
    to_representation: spec.TimefrequencyRepresentation | None = None,
) -> spec.Timefrequency:
    """create Timefrequency

    ## Inputs
    - frequency: TimeFrequency
    - count: int or float count
    - per: TimeLength
    - interval: TimeLength
    - to_representation: str name of Timefrequency representation

    ## Returns
    - Timeperiod with specified representation
    """

    if to_representation is None:
        to_representation = 'TimefrequencyFrequency'

    if to_representation == 'TimefrequencyFrequency':
        return create_timefrequency_frequency(
            frequency=frequency,
            count=count,
            per=per,
            interval=interval,
        )
    elif to_representation == 'TimefrequencyCountPer':
        return create_timefrequency_count_per(
            frequency=frequency,
            count=count,
            per=per,
            interval=interval,
        )
    elif to_representation == 'TimefrequencyInterval':
        return create_timefrequency_interval(
            frequency=frequency,
            count=count,
            per=per,
            interval=interval,
        )
    else:
        raise Exception(
            'unknown timefrequency representation: ' + str(to_representation)
        )


def create_timefrequency_frequency(
    frequency: int | float | None = None,
    count: int | float | None = None,
    per: spec.Timelength | None = None,
    interval: spec.Timelength | None = None,
) -> spec.TimefrequencyFrequency:
    """create Timefrequency with representation TimefrequencyFrequency

    ## Inputs
    - frequency: TimeFrequency
    - count: int or float count
    - per: TimeLength
    - interval: TimeLength

    ## Returns
    - TimefrequencyFrequency
    """

    if frequency is not None:
        return frequency
    elif count is not None and per is not None:
        per_seconds = timelength_utils.timelength_to_seconds(per)
        return float(count) / float(per_seconds)
    elif interval is not None:
        interval_seconds = timelength_utils.timelength_to_seconds(interval)
        return 1 / float(interval_seconds)
    else:
        raise Exception('specify either frequency, interval, or count and per')


def create_timefrequency_count_per(
    frequency: int | float | None = None,
    count: int | float | None = None,
    per: spec.Timelength | None = None,
    interval: spec.Timelength | None = None,
) -> spec.TimefrequencyCountPer:
    """create Timefrequency with representation TimefrequencyCountPer

    ## Inputs
    - frequency: TimeFrequency
    - count: int or float count
    - per: TimeLength
    - interval: TimeLength

    ## Returns
    - TimefrequencyCountPer
    """

    if frequency is not None:
        return {'count': frequency, 'per': 1}
    if count is not None and per is not None:
        return {'count': count, 'per': per}
    elif interval is not None:
        return {'count': 1, 'per': interval}
    else:
        raise Exception('specify either frequency, interval, or count and per')


def create_timefrequency_interval(
    frequency: int | float | None = None,
    count: int | float | None = None,
    per: spec.Timelength | None = None,
    interval: spec.Timelength | None = None,
) -> spec.TimefrequencyInterval:
    """create Timefrequency with representation TimefrequencyInterval

    ## Inputs
    - frequency: TimeFrequency
    - count: int or float count
    - per: TimeLength
    - interval: TimeLength

    ## Returns
    - TimefrequencyInterval
    """

    if frequency is not None:
        return {'interval': 1 / float(frequency)}
    elif count is not None and per is not None:
        per_seconds = timelength_utils.timelength_to_seconds(per)
        return {'interval': per_seconds / float(count)}
    elif interval is not None:
        return {'interval': interval}
    else:
        raise Exception('specify either frequency, interval, or count and per')
