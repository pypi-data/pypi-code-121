from __future__ import annotations

import typing
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    import numpy as np

from .. import timelength_utils


class TimeFrequencyResolution(TypedDict):
    label: str
    dts: typing.Sequence[typing.SupportsInt | typing.SupportsFloat]
    use_n: int | None
    median_dt: float
    outliers: TimeFrequencyResolutionOutliers


class TimeFrequencyResolutionOutliers(TypedDict):
    small: np.ndarray
    large: np.ndarray
    outlier_rtol: float


def detect_resolution(
    timestamps: typing.Sequence[typing.SupportsInt | typing.SupportsFloat],
    use_n: int | None = None,
    outlier_rtol: float = 0.5,
) -> TimeFrequencyResolution | None:
    """detect resolution of iterable of Timestamps

    ## Detection Algorithm
    - current algorithm: whether median dt value is close to a known value
    - dts that are +- 50% of this median are returned in 'outliers' key

    ## Inputs
    - timestamps: iterable of Timestamp
    - use_n: int or None, indicating number of timestamp values to use
        - smaller n will be faster but could be less representative
    - outlier_rtol: float of tolerance for detecting outliers
    """

    try:
        import numpy as np
    except ImportError:
        raise Exception('numpy required for resolution detection')

    if len(timestamps) == 1:
        return None

    # preprocess
    if isinstance(timestamps, np.ndarray):
        timestamps_array = timestamps
    else:
        timestamps_array = np.array(timestamps)
    if use_n is not None:
        timestamps_array = timestamps_array[:use_n]

    # compute time deltas
    dts = timestamps_array[1:] - timestamps_array[:-1]
    median_dt = np.median(dts)
    outliers: TimeFrequencyResolutionOutliers = {
        'small': dts[dts < 1 / (1 + outlier_rtol) * median_dt],
        'large': dts[dts > (1 + outlier_rtol) * median_dt],
        'outlier_rtol': outlier_rtol,
    }

    label = timelength_utils.timelength_seconds_to_label(median_dt)

    return {
        'label': label,
        'dts': dts,
        'use_n': use_n,
        'median_dt': median_dt,
        'outliers': outliers,
    }
