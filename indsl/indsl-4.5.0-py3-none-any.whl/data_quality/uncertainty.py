# Copyright 2022 Cognite AS

from typing import Optional

import pandas as pd

from indsl.filter import trend_extraction_hilbert_transform
from indsl.validations import validate_series_has_time_index


def uncertainty_rstd(
    data: pd.Series,
    resample_rate: pd.Timedelta = pd.Timedelta("30m"),
    emd_sift_thresh: float = 1e-8,
    emd_max_num_imfs: Optional[int] = None,
    emd_error_tolerance: float = 0.05,
) -> pd.Series:
    """Relative uncertainty

    The relative uncertainty is computed as the ratio between the
    standard deviation of the signal noise and the mean of the true signal.
    The noise and true signals are estimated using the empirical model decomposition method.
    The relative uncertainty is computed on segments of the input data of size
    rst_resample_rate. In mathematical notation, this means:

    .. math::

        rstd = \\sigma(F_t - A_t)/|\\mu(A_t)|

    where :math:`F_t` is the resampled input time series, and :math:`A_t` is the resampled and
    detrended time series obtained using the empirical model decomposition method (EMD).

    Args:
        data: Time series
            Input time series
        resample_rate: Resample rate
            Resample rate used when estimating the relative standard deviation
        emd_sift_thresh: Sifting threshold
            Threshold to stop EMD sifting process. This threshold is based on the Cauchy convergence test and represents the
            residue between two consecutive oscillatory components (IMFs). A small threshold (close to zero) will
            result in more components extracted. Typically, a few IMFs are enough to build the main trend. Choosing a
            high threshold might not affect the outcome. Defaults to 1e-8.
        emd_max_num_imfs: Maximum number of components
            Maximum number of EMD oscillatory components (or IMFs) to estimate the main trend. If no value (None) is defined
            the process continues until sifting threshold is reached. Defaults to None.
        emd_error_tolerance: Energy tolerance
            Threshold for the EMD cross energy ratio validation used for choosing oscillatory components or IMFs. Defaults to
            0.05.

    Returns:
        pd.Series: Time series
    """
    validate_series_has_time_index(data)

    # Estimate the true signal and its noise using EDM
    truth = trend_extraction_hilbert_transform(data, emd_sift_thresh, emd_max_num_imfs, emd_error_tolerance)
    noise = data - truth

    noise_std = noise.resample(resample_rate, origin="start").std().reindex(truth.index, method="ffill").interpolate()
    truth_mean = truth.resample(resample_rate, origin="start").mean().reindex(truth.index, method="ffill").interpolate()

    relative_std = (noise_std / abs(truth_mean)).dropna()
    return relative_std
