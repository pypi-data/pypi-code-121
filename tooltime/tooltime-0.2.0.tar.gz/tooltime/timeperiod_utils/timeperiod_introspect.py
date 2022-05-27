from __future__ import annotations

import typing

from .. import spec
from .. import timestamp_utils
from . import timeperiod_convert


def print_timeperiod(
    timeperiod: spec.Timeperiod,
    timestamp_representation: spec.TimestampRepresentation = 'TimestampLabel',
    print_kwargs: dict[str, typing.Any] = None,
) -> None:
    """print Timeperiod

    ## Inputs
    - timeperiod: Timeperiod
    - timestamp_representation: str name of Timestamp representation to print
    - print_kwargs: kwargs passed to print()
    """

    start, end = timeperiod_convert.timeperiod_to_pair(timeperiod)
    start_label = timestamp_utils.convert_timestamp(
        start,
        to_representation=timestamp_representation,
    )
    end_label = timestamp_utils.convert_timestamp(
        end,
        to_representation=timestamp_representation,
    )

    if print_kwargs is None:
        print_kwargs = {}
    print('[' + str(start_label) + ', ' + str(end_label) + ']', **print_kwargs)

