# Copyright 2021 Cognite AS
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from numba import njit
from scipy.fft import fft, fftfreq
from scipy.signal import argrelextrema, lfilter

from ..exceptions import UserTypeError, UserValueError
from ..type_check import check_types


@check_types
def oscillation_detector(data: pd.Series, order: int = 4, threshold: float = 0.2) -> Dict:
    """Oscillations

    Identifies if a signal contains one or more oscillatory components. Based on the paper by Sharma et. al. [#]_.

    The method uses Linear Predictive Coding (LPC) and is implemented as a 3 step process:

        1. Estimate the LPC coefficients from the prediction polynomial. These are used to estimate a fit to the
           data
        2. Estimate the roots of the LPC coefficients
        3. Estimate the distance of each root to the unit circle in the complex plane

    If the distance of any root is close to the unit circle (less than 0.2) the signal is considered to have an
    oscillatory component


    Args:
        data: Time series
        order: Polynomial order
            Order of the prediction polynomial. Defaults to 4.
        threshold: Threshold
            Maximum distance of a root to the unit circle for which the signal is considered to have an oscillatory
            component. Defaults to 0.2

    Returns:
        dict: Dictionary with the following keys and values::

            {
                "roots": np.ndarray,
                "distances": np.ndarray,
                "PSD": dict:  {"f": np.ndarray, "Pxx": np.ndarray},
                "fit": dict: {"time": np.ndarray, "data": np.ndarray},
                "oscillations": bool,
                "peaks": dict: {"f": np.ndarray, "amplitude": np.ndarray,}
            }

        Return dictionary elaboration:

        - roots -> roots of the predicted LPC coefficients
        - distances -> distance of each root to the unit circle
        - PSD -> Power spectral density, frequency and power vector
        - fit -> fitted data using the LPC prediction polynomial
        - oscillations -> (1) Oscillation detected, (0) no oscillatory component detected
        - peaks -> Peak frequencies and corresponding amplitudes in original data.

    Warnings:
        Large variations in sampling time may affect the proficiency of the algorithm. Works best on time series with
        uniform sampling frequency. If non-uniformly sampled, we suggest using a resampling method to fill the missing
        data.

    Raises:
        RuntimeError: Length of interpolated data does not match predicted data.

    References:
        .. [#] Sharma et al. "Automatic signal detection and quantification in process control loops using linear
               predictive coding." Eng. Sc. & Tech. an Intnl. Journal 2020.
    """

    time = np.array([item.value / 1e9 for item in data.index])
    data = data.to_numpy()

    # Resample with frequency equal to average frequency into uniformly sampled data
    # In most asset-heavy industrial data, the sampling frequency
    # is non-uniform and sampling intervals range from a couple of seconds to minutes
    # In some cases the sampling interval can be longer than minutes. In that case the method could fail

    delta_t = np.median(np.diff(time))  # Sampling interval
    time_interp = np.linspace(time[0], time[-1], num=len(time))
    data_interp = np.interp(time_interp, time, data)

    # Estimate LPC and generate prediction polynomial
    lpc_arr = lpc(data_interp, order)  # First coefficient is always 1
    data_predicted = lfilter(-lpc_arr[1:], [1], data_interp)  # Predicted data fit

    if len(data_interp) != len(data_predicted):
        raise RuntimeError(
            f"Something went wrong! The length of the interpolated ({len(data_interp)}) and predicted data"
            f" ({len(data_predicted)}) are different"
        )

    # Replace initial output from the filter (outliers)
    # This is to avoid large deviations in the initial prediction introduced by the filter
    data_interp_std = np.std(data_interp)
    for i, (pred, interp) in enumerate(zip(data_predicted, data_interp)):
        if abs(pred - interp) > data_interp_std:
            data_predicted[i] = interp
        else:
            break

    roots = np.roots(lpc_arr)
    distances = 1 - abs(roots)

    # Verify if signal were detected. Any distance below given threshold (close to the unit circle. default 0.2)
    # means that an oscillatory component was detected
    detected = any(distances < threshold)

    # Obtain power spectral density of signal
    n = len(data_interp)
    data_interp_fft = fft(data_interp)
    amplitude = 2 * np.abs(data_interp_fft)[: n // 2] / n
    data_freqs = fftfreq(n, delta_t)
    data_freqs = data_freqs[: n // 2]

    # Build results dictionary and plot if requested
    results = {
        "roots": roots,
        "distances": distances,
        "PSD": {"f": data_freqs, "Pxx": amplitude},
        "fit": {"time": time_interp, "data": data_predicted},
        "oscillations": detected,
        "peaks": {},
    }

    # If oscillations detected find amplitude of peak frequencies, and plot if requested.
    if detected:
        residuals = data_interp - data_predicted
        peaks = _peak_freq_components(residuals, data_interp, delta_t)

        results["peaks"] = peaks

    return results


def _peak_freq_components(residuals: np.ndarray, data: np.ndarray, dt: float) -> Dict:
    """
    Find the peak frequency components of a signal identified as having oscillation via the LPC method.

    Args:
        residuals: residuals from the predicted LPC analysis.
        data: signal. It's assumed the data is uniformly sampled (constant sampling interval)
        dt: sampling interval.

    Returns:
        (dict, dict): tuple of two dictionaries where the first contain peak frequencies and amplitudes and the second
                      contains figure components
    """
    lags, xcoef = cross_corr(residuals, data)

    # Remove negative lags and subtract its mean
    mask = lags >= 0
    xcoef = xcoef[mask]
    lags = lags[mask]
    xcoef -= np.mean(xcoef)

    # Compute FFT of correlation coefficients and normalize with max peak
    power_norm = np.abs(fft(xcoef))
    power_norm /= np.max(power_norm)
    n = len(power_norm)
    freqs = fftfreq(n, dt)

    # Remove half of the results as they are the mirrored
    power_norm = power_norm[: n // 2]
    freqs = freqs[: n // 2]

    # Locate peak frequencies
    peaks_loc = argrelextrema(np.where(power_norm > 0.3, power_norm, [0]), np.greater)[0]
    peak_freqs = freqs[peaks_loc]

    # FFT spectrum of original signal
    n1 = len(data)
    data_fft = fft(data)
    amplitude = 2 * np.abs(data_fft)[: n1 // 2] * 1 / n1
    data_freqs = fftfreq(n1, dt)
    amplitude_index = [np.where(data_freqs[: n1 // 2] == peak_freq)[0][0] for peak_freq in peak_freqs]
    peak_amplitude = amplitude[amplitude_index]

    peaks = {"f": peak_freqs, "amplitude": peak_amplitude}

    return peaks


def _validate_data(y: np.ndarray):
    if not np.issubdtype(y.dtype, np.floating):
        raise UserTypeError("Data must be floating-point")

    if y.ndim != 1:
        raise UserTypeError(f"Signal data must have shape (samples,). Received shape={y.shape}")

    if np.isnan(y).any() or np.isinf(y).any():
        raise UserTypeError("Signal is not finite everywhere or contains one or more NaNs")

    if np.all(y[0] == y[1:]):
        raise UserValueError("Ill-conditioned input array; contains only one unique value")


def lpc(y: np.ndarray, order: int) -> np.ndarray:
    """
    The code is adapted from https://github.com/librosa/librosa/blob/main/librosa/core/audio.py

    Librosa is licensed under the ISC License:

        Copyright (c) 2013--2017, librosa development team.

        Permission to use, copy, modify, and/or distribute this software for any
        purpose with or without fee is hereby granted, provided that the above
        copyright notice and this permission notice appear in all copies.

        THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
        WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
        MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
        ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
        WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
        ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
        OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

    Linear Prediction Coefficients via Burg's method

        This function applies Burg's method to estimate coefficients of a linear
        filter on ``y`` of order ``order``.  Burg's method is an extension to the
        Yule-Walker approach, which are both sometimes referred to as LPC parameter
        estimation by autocorrelation.

        It follows the description and implementation approach described in the
        introduction by Marple. [#]_  N.B. This paper describes a different method, which
        is not implemented here, but has been chosen for its clear explanation of
        Burg's technique in its introduction.

        .. [#] Larry Marple.
               A New Autoregressive Spectrum Analysis Algorithm.
               IEEE Transactions on Accoustics, Speech, and Signal Processing
               vol 28, no. 4, 1980.

    Args:
        y: Uniformly sampled signal data.
        order: Order of the prediction polynomial. Hence number of LPC coefficients.

    Returns:
        np.ndarray: LPC coefficients.
    """

    if not isinstance(order, int) or order < 1:
        raise UserValueError("order must be an integer > 0")

    _validate_data(y)

    return _lpc(y, order)


@njit
def _lpc(y: np.ndarray, order: int) -> np.ndarray:
    # This implementation follows the description of Burg's algorithm given in
    # section III of Marple's paper referenced in the docstring.
    #
    # We use the Levinson-Durbin recursion to compute AR coefficients for each
    # increasing model order by using those from the last. We maintain two
    # arrays and then flip them each time we increase the model order so that
    # we may use all the coefficients from the previous order while we compute
    # those for the new one. These two arrays hold ar_coeffs for order M and
    # order M-1.  (Corresponding to a_{M,k} and a_{M-1,k} in eqn 5)

    dtype = y.dtype.type
    ar_coeffs = np.zeros(order + 1, dtype=dtype)
    ar_coeffs[0] = dtype(1)
    ar_coeffs_prev = np.zeros(order + 1, dtype=dtype)
    ar_coeffs_prev[0] = dtype(1)

    # These two arrays hold the forward and backward prediction error. They
    # correspond to f_{M-1,k} and b_{M-1,k} in eqns 10, 11, 13 and 14 of
    # Marple. First they are used to compute the reflection coefficient at
    # order M from M-1 then are re-used as f_{M,k} and b_{M,k} for each
    # iteration of the below loop
    fwd_pred_error = y[1:]
    bwd_pred_error = y[:-1]

    # DEN_{M} from eqn 16 of Marple.
    den = np.dot(fwd_pred_error, fwd_pred_error) + np.dot(bwd_pred_error, bwd_pred_error)

    for i in range(order):
        if den <= 0:
            raise FloatingPointError("numerical error, input ill-conditioned?")

        # Eqn 15 of Marple, with fwd_pred_error and bwd_pred_error
        # corresponding to f_{M-1,k+1} and b{M-1,k} and the result as a_{M,M}
        # reflect_coeff = dtype(-2) * np.dot(bwd_pred_error, fwd_pred_error) / dtype(den)
        reflect_coeff = dtype(-2) * np.dot(bwd_pred_error, fwd_pred_error) / dtype(den)

        # Now we use the reflection coefficient and the AR coefficients from
        # the last model order to compute all of the AR coefficients for the
        # current one.  This is the Levinson-Durbin recursion described in
        # eqn 5.
        # Note 1: We don't have to care about complex conjugates as our signals
        # are all real-valued
        # Note 2: j counts 1..order+1, i-j+1 counts order..0
        # Note 3: The first element of ar_coeffs* is always 1, which copies in
        # the reflection coefficient at the end of the new AR coefficient array
        # after the preceding coefficients
        ar_coeffs_prev, ar_coeffs = ar_coeffs, ar_coeffs_prev
        for j in range(1, i + 2):
            ar_coeffs[j] = ar_coeffs_prev[j] + reflect_coeff * ar_coeffs_prev[i - j + 1]

        # Update the forward and backward prediction errors corresponding to
        # eqns 13 and 14.  We start with f_{M-1,k+1} and b_{M-1,k} and use them
        # to compute f_{M,k} and b_{M,k}
        fwd_pred_error_tmp = fwd_pred_error
        fwd_pred_error = fwd_pred_error + reflect_coeff * bwd_pred_error
        bwd_pred_error = bwd_pred_error + reflect_coeff * fwd_pred_error_tmp

        # SNIP - we are now done with order M and advance. M-1 <- M

        # Compute DEN_{M} using the recursion from eqn 17.
        #
        # reflect_coeff = a_{M-1,M-1}      (we have advanced M)
        # den =  DEN_{M-1}                 (rhs)
        # bwd_pred_error = b_{M-1,N-M+1}   (we have advanced M)
        # fwd_pred_error = f_{M-1,k}       (we have advanced M)
        # den <- DEN_{M}                   (lhs)
        #

        q = dtype(1) - reflect_coeff**2
        den = q * den - bwd_pred_error[-1] ** 2 - fwd_pred_error[0] ** 2

        # Shift up forward error.
        #
        # fwd_pred_error <- f_{M-1,k+1}
        # bwd_pred_error <- b_{M-1,k}
        #
        # N.B. We do this after computing the denominator using eqn 17 but
        # before using it in the numerator in eqn 15.
        fwd_pred_error = fwd_pred_error[1:]
        bwd_pred_error = bwd_pred_error[:-1]

    return ar_coeffs


def cross_corr(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes between signal x and y correlation for different lags and returns corresponding lag and correlation
    coefficients

    Args:
        x: Signal 1
        y: Signal 2

    Returns:
        (np.ndarray, np.ndarray): Lags and correlation coefficients

    """
    x, y = map(np.asarray, (x, y))
    n = x.size  # think n is better than lx which refers to one of the two variables
    if n != y.size:
        raise UserValueError("x and y must be equal length")

    lags_num = n - 1

    if lags_num >= n or lags_num < 1:
        raise UserValueError(f"lags must be None or strictly positive < {n}")

    corr_coeffs = np.correlate(x, y, mode="full")

    lags = np.arange(-lags_num, lags_num + 1)
    start_idx, end_idx = n - 1 - lags_num, n + lags_num
    corr_coeffs = corr_coeffs[start_idx:end_idx]

    return lags, corr_coeffs
