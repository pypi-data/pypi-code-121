import typing

from .. import spec
from .. import timelength_utils
from . import timeperiod_crud


def timeperiods_overlap(
    timeperiod_lhs: spec.Timeperiod, timeperiod_rhs: spec.Timeperiod
) -> bool:
    """return bool of whether timeperiods have any overlap"""
    start_lhs, end_lhs = timeperiod_crud.compute_timeperiod_start_end(
        timeperiod_lhs
    )
    start_rhs, end_rhs = timeperiod_crud.compute_timeperiod_start_end(
        timeperiod_rhs
    )
    return (start_lhs <= start_rhs <= end_lhs) or (
        start_lhs <= end_rhs <= end_lhs
    )


def timeperiod_contains(
    timeperiod: spec.Timeperiod,
    other_timeperiod: spec.Timeperiod,
) -> bool:
    """return bool of whether timeperiod contains other timeperiod"""
    start, end = timeperiod_crud.compute_timeperiod_start_end(timeperiod)
    other_start, other_end = timeperiod_crud.compute_timeperiod_start_end(
        other_timeperiod
    )
    return (start <= other_start) and (end >= other_end)


def create_superset_timeperiod(
    *timeperiods: spec.Timeperiod,
) -> spec.Timeperiod:
    """create Timeperiod that contains all input Timeperiods"""
    min_start = float('inf')
    max_end = float('-inf')
    for timeperiod in timeperiods:
        start, end = timeperiod_crud.compute_timeperiod_start_end(timeperiod)
        if start < min_start:
            min_start = start
        if end > max_end:
            max_end = end
    return (min_start, max_end)


def create_overlapping_timeperiod(
    timeperiod: spec.Timeperiod,
    trim_start_relative: typing.SupportsFloat = None,
    trim_end_relative: typing.SupportsFloat = None,
    trim_start_absolute: spec.Timelength = None,
    trim_end_absolute: spec.Timelength = None,
    extend_start_relative: typing.SupportsFloat = None,
    extend_end_relative: typing.SupportsFloat = None,
    extend_start_absolute: spec.Timelength = None,
    extend_end_absolute: spec.Timelength = None,
) -> spec.Timeperiod:
    """create copy of timeperiod with start or end trimmed or extended

    - can trim or end by relative or absolute amount

    ## Inputs
    - timeperiod: Timeperiod
    - trim_start_relative: float relative amount of length to trim at start
    - trim_end_relative: float relative amount of length to trim at end
    - trim_start_absolute: Timelength amount of time to trim at start
    - trim_end_absolute: Timelength amount of time to trim at end
    - extend_start_relative: float relative amount of length to extend at start
    - extend_end_relative: float relative amount of length to extend at end
    - extend_start_absolute: Timelength amount of time to extend at start
    - extend_end_absolute: Timelength amount of time to extend at end
    """

    start, end = timeperiod_crud.compute_timeperiod_start_end(timeperiod)
    length = end - start
    new_start = start
    new_end = end

    # trim boundaries
    if trim_start_relative is not None:
        new_start = new_start + spec.to_numeric(trim_start_relative) * length
    if trim_end_relative is not None:
        new_end = new_end - spec.to_numeric(trim_end_relative) * length
    if trim_start_absolute is not None:
        trim_start_seconds = timelength_utils.timelength_to_seconds(
            trim_start_absolute
        )
        new_start = new_start + trim_start_seconds
    if trim_end_absolute is not None:
        trim_end_seconds = timelength_utils.timelength_to_seconds(
            trim_end_absolute
        )
        new_end = new_end - trim_end_seconds

    # extend boundaries
    if extend_start_relative is not None:
        new_start = new_start - spec.to_numeric(extend_start_relative) * length
    if extend_end_relative is not None:
        new_end = new_end + spec.to_numeric(extend_end_relative) * length
    if extend_start_absolute is not None:
        extend_start_seconds = timelength_utils.timelength_to_seconds(
            extend_start_absolute
        )
        new_start = new_start - extend_start_seconds
    if extend_end_absolute is not None:
        extend_end_seconds = timelength_utils.timelength_to_seconds(
            extend_end_absolute
        )
        new_end = new_end + extend_end_seconds

    return (new_start, new_end)

