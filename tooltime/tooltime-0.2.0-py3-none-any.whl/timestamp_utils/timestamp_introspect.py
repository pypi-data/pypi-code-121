from __future__ import annotations

import typing

from .. import spec
from .. import timefrequency_utils
from .. import timelength_utils
from . import timestamp_convert


def summarize_timestamps(
    timestamps: typing.Sequence[spec.Timestamp],
) -> spec.TimestampSummary:
    """create summary of timestamps

    ## Inputs
    - timestamps: iterable of Timestamp
    """

    timestamps_precise: typing.List[spec.TimestampSecondsPrecise] = []
    for timestamp in timestamps:
        precise = timestamp_convert.timestamp_to_seconds_precise(timestamp)
        timestamps_precise.append(precise)

    n_t = len(timestamps)
    summary: spec.TimestampSummary = {'n_t': n_t}

    if n_t == 1:
        summary['start'] = timestamps_precise[0]
        summary['end'] = timestamps_precise[0]

    elif n_t > 1:
        if timestamps_precise[-1] < timestamps_precise[0]:
            timestamps_precise = timestamps_precise[::-1]

        n_unique = len(set(timestamps_precise))
        resolution = timefrequency_utils.detect_resolution(timestamps_precise)
        if resolution is None:
            raise Exception('could not detect resolution')
        start = timestamp_convert.timestamp_to_label(timestamps_precise[0])
        end = timestamp_convert.timestamp_to_label(timestamps_precise[-1])
        duration = timestamps_precise[-1] - timestamps_precise[0]
        duration_label = timelength_utils.timelength_seconds_to_clock_phrase(
            duration
        )
        n_large_outliers = resolution['outliers']['large'].shape[0]
        n_small_outliers = resolution['outliers']['small'].shape[0]
        n_outliers = n_large_outliers + n_small_outliers

        if resolution['median_dt'] > 0.0001:
            import numpy as np

            n_ideal_iter = np.arange(
                timestamps_precise[0],
                timestamps_precise[-1] + resolution['median_dt'],
                resolution['median_dt'],
            )
            n_ideal = list(n_ideal_iter)
            summary['n_missing'] = len(n_ideal) - len(timestamps_precise)
        else:
            summary['n_missing'] = None

        summary['n_unique'] = n_unique
        summary['resolution'] = resolution
        summary['start'] = start
        summary['end'] = end
        summary['duration'] = duration
        summary['duration_label'] = duration_label
        summary['n_large_outliers'] = n_large_outliers
        summary['n_small_outliers'] = n_small_outliers
        summary['n_outliers'] = n_outliers

    return summary


def print_timestamp_summary(
    *,
    timestamps: typing.List[spec.Timestamp] = None,
    summary: typing.Optional[spec.TimestampSummary] = None,
    indent: typing.Optional[str] = None,
    print_kwargs: dict[str, typing.Any] = None
) -> None:
    """print summary of timestamps

    - specify either timestamps or summary
    - timestamps should be ordered
        - todo: do not require ordering

    ## Inputs
    - timestamps: iterable of Timestamp
    - summary: dict summary created by summarize_timestamps()
    - indent: str indent of each line in summary
    - print_kwargs: kwargs passed to print()
    """

    # validate inputs
    if indent is None:
        indent = ''
    if print_kwargs is None:
        print_kwargs = {}

    # create summary if not provided
    if summary is None:
        if timestamps is None:
            raise Exception('must specify timestamps or summary')
        summary = summarize_timestamps(timestamps)

    n_t = summary['n_t']
    print(indent + 'n_t:', n_t, **print_kwargs)

    if n_t == 1:
        print(indent + 'timestamp:', summary['start'], **print_kwargs)

    elif n_t > 1:

        n_unique = summary['n_unique']
        resolution = summary['resolution']
        start = summary['start']
        end = summary['end']
        duration = summary['duration']
        duration_label = summary['duration_label']
        n_large_outliers = summary['n_large_outliers']
        n_small_outliers = summary['n_small_outliers']
        n_outliers = summary['n_outliers']
        n_missing = summary['n_missing']
        outlier_rtol = resolution['outliers']['outlier_rtol']
        mean_dt = timelength_utils.timelength_to_label(duration / (n_t - 1))

        print(indent + 'n_unique:', n_unique, **print_kwargs)
        print(indent + 'extent:')
        print(
            '    ' + indent + 'start:',
            start,
            '(' + ('%.14g' % summary['start']) + ')',
            **print_kwargs
        )
        print(
            '    ' + indent + 'end:  ',
            end,
            '(' + ('%.14g' % summary['end']) + ')',
            **print_kwargs
        )
        print(
            '    ' + indent + 'duration:',
            duration_label,
            '(' + ('%.14g' % duration) + ' s)',
            **print_kwargs
        )
        print(indent + 'resolution:', **print_kwargs)
        print(
            '    ' + indent + 'median_dt:', resolution['label'], **print_kwargs
        )
        print('    ' + indent + 'mean_dt:', mean_dt, **print_kwargs)
        print(
            '    ' + indent + 'missing timestamps:',
            n_missing,
            '(if median_dt maintained)',
            **print_kwargs
        )
        print('    ' + indent + 'outlier_dts:', n_outliers, **print_kwargs)
        print(
            '        ' + indent + 'small:',
            n_small_outliers,
            '       dt < median_dt / (1 + outlier_rtol)',
            **print_kwargs
        )
        print(
            '        ' + indent + 'large:',
            n_large_outliers,
            '       dt > median_dt * (1 + outlier_rtol)',
            **print_kwargs
        )
        print(
            '        ' + indent + '(outlier_rtol =',
            str(outlier_rtol) + ')',
            **print_kwargs
        )

