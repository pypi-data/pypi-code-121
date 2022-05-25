from typing import Optional

import emd
import numpy as np
import pandas as pd

from indsl.ts_utils import get_timestamps

from ..exceptions import UserValueError
from ..type_check import check_types
from ..validations import validate_series_has_minimum_length


MIN_DATA_PT = 10


@check_types
def trend_extraction_hilbert_transform(
    series: pd.Series,
    sift_thresh: float = 1e-8,
    max_num_imfs: Optional[int] = None,
    error_tolerance: float = 0.05,
    return_trend: bool = True,
) -> pd.Series:
    """Trend / De-trend signal

    Robust method to determine the trend of any non-linear and non-stationary time series based on the `Hilbert-Huang
    Transform and empirical mode decomposition (EMD). This is a mathematically complex method and not easy to document
    in detail. If you are interested in knowing more about it see following the list of resources:

        * `EMD wiki <https://en.wikipedia.org/wiki/Hilbert%E2%80%93Huang_transform>`_
        * `Trend extraction based on the Hilbert-Huang transform and Empirical Mode Decomposition
          <https://www.researchgate.net/publication/261234992_Trend_extraction_based_on_Hilbert-Huang_transform>`_
        * `EMD Python package <https://emd.readthedocs.io/en/stable/>`_ with useful examples
          and tutorials
        * `Article on EMD implementation <https://www.pnas.org/doi/full/10.1073/pnas.0701020104>`_ and
          applied to global surface temperature anomalies data set

    The EMD method decomposes a time series into a finite number of oscillatory components, each with a
    well defined frequency and amplitude. These are called intrinsic mode functions (IMFs). The process to identify
    IMFs is called sifting (i.e. filtering). The sift works by iteratively extracting oscillatory components from a
    signal. Starting from the fastest and through to the very slowest until the average envelope of the components
    is less than the sifting threshold.

    The number of components selected for building the main trend are selected using the cross energy ration
    between IMFs using the Hilbert-Huang transform to estimate the spectra. If the ratio is below a given energy
    tolerance threshold, the process stops and the selected IMFs are added together. That is the resulting main trend.

    As an output, it is possible to select either the trend of the main signal or the de-trended signal.

    Args:
        series: Time series
        sift_thresh: Sifting threshold
            Threshold to stop sifting process. This threshold is based on the Cauchy convergence test and represent the
            residue between two consecutive oscillatory components (IMFs). A small threshold (close to zero) will
            result in more components extracted. Typically, a few IMFs are enough to build the main trend. Choosing a
            high threshold might not affect the outcome. Defaults to 1e-8.
        max_num_imfs: Maximum number of components
            Maximum number of oscillatory components (or IMFs) to estimate the main trend. If no value (None) is defined
            the process continues until sifting threshold is reached. Defaults to None.
        error_tolerance: Energy tolerance
            Threshold for cross energy ratio validation used for choosing oscillatory components or IMFs. Defaults to
            0.05.
        return_trend: Output trend
            Output the trend if true. Remove the trend from the time series if False. Defaults to True.

    Returns:
        pd.Series: Time series
    """

    validate_series_has_minimum_length(series, MIN_DATA_PT)

    if error_tolerance <= 0:
        raise UserValueError("The energy tolerance  must be higher than zero")
    if max_num_imfs is not None and max_num_imfs <= 0:
        raise UserValueError("The maximum number of oscillatory components must be an integer higher than zero")
    if sift_thresh <= 0:
        raise UserValueError("The Sifting threshold must be a number higher than zero")

    # compute IMFs
    imf = emd.sift.sift(series.values, sift_thresh, max_num_imfs)
    total_number_of_imf: int = imf.shape[1]
    index_of_the_last_imf: int = total_number_of_imf - 1

    # find sampling rate in Hz
    timestamps = get_timestamps(series, "s")
    sample_rate_hz = 1 / (np.mean(np.diff(timestamps.values)))

    # compute phase, frequency and amplitude
    phase, frequency, amplitude = emd.spectra.frequency_transform(imf, sample_rate=sample_rate_hz, method="hilbert")

    # compute Hilbert-Huang spectrum for each IMF separately and sum over time to get Hilbert marginal spectrum
    ff, hht = emd.spectra.hilberthuang(frequency, amplitude, sum_imfs=False, sample_rate=sample_rate_hz)

    # compute cross energy ratio
    significant_imf_index: int = index_of_the_last_imf

    for i in range(index_of_the_last_imf - 1, -1, -1):
        rho = np.sum(hht[:, i] * hht[:, i + 1]) / (np.sum(hht[:, i]) * np.sum(hht[:, i + 1]))

        if rho < error_tolerance:
            break
        else:
            significant_imf_index = significant_imf_index - 1

    trend = sum(imf[:, i] for i in range(significant_imf_index, total_number_of_imf))

    trend_series = pd.Series(trend, index=series.index)

    return trend_series if return_trend else series - trend_series
