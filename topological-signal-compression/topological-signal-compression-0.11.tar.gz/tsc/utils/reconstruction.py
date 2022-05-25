# Gary Koplik
# gary<dot>koplik<at>geomdata<dot>com
# March, 2022
# reconstruction.py

"""
Methods for doing *just* reconstruction of compressed signals using the counterfactual compression methods.
For more on the compression methods, see the :py:mod:`tsc.utils.compression` module.

Note, the Topological Signal Compression (TSC) method is under :py:func:`~tsc.__init__.reconstruct_tsc()`.
"""


import numpy as np
from pydub import AudioSegment
from pyts.utils.utils import segmentation
from tsc import reconstruct_tsc
from tsc.utils.helper_functions import min_max_normalize, pydub_to_numpy


def reconstruct_dft(fourier_coefficients: np.ndarray, size: int) -> np.ndarray:
    """
    Reconstructs a signal from the shape ``(n, )`` array of Fourier coefficients output from
    :py:func:`tsc.utils.compression.compress_dft()`.
    Reconstructs the signal with linear interpolation to be back to its original ``size``.
    This is useful when feeding a reconstructed signal into a machine learning pipeline expecting a specifically-sized
    input.

    Code adapted from the
    `pyts package <https://pyts.readthedocs.io/en/stable/auto_examples/approximation/plot_dft.html>`_.

    :param fourier_coefficients: shape ``(n, )`` array of Fourier Coefficients to use to reconstruct the signal.
    :param size: size of the original array being reconstructed (e.g. number of time steps).
    :return: shape ``(size, )`` np.array of the reconstructed signal.
    :rtype: ``np.ndarray``.
    """

    # play nice with expected shapes for adapted code
    arr = fourier_coefficients.reshape(1, -1)

    if arr.size % 2 == 0:
        real_idx = np.arange(1, arr.size, 2)
        imag_idx = np.arange(2, arr.size, 2)
        arr_new = np.c_[
            arr[:, :1],
            arr[:, real_idx] + 1j * np.c_[arr[:, imag_idx],
                                          np.zeros((1,))]
        ]
    else:
        real_idx = np.arange(1, arr.size, 2)
        imag_idx = np.arange(2, arr.size + 1, 2)
        arr_new = np.c_[
            arr[:, :1],
            arr[:, real_idx] + 1j * arr[:, imag_idx]
        ]
    x_irfft = np.fft.irfft(arr_new,
                           size
                           )

    return x_irfft.flatten()


def reconstruct_opus(filepath: str, sampling_rate: int = 8000) -> np.ndarray:
    """
    Read in Opus-compressed results from one file.

    :param filepath: path to compression data for single signal.
    :param sampling_rate: sampling rate of original signal.
    :return: 1d array of the linearly interpolated signal.
    :rtype: ``np.ndarray``.
    """

    sample = AudioSegment.from_ogg(filepath).set_frame_rate(sampling_rate)
    output = min_max_normalize(pydub_to_numpy(sample))

    return output


def reconstruct_paa(signal: np.ndarray, original_signal_size: int, window_size: int) -> np.ndarray:
    """
    Reconstructs a signal from the shape ``(n, )`` array of a compressed signal output from the
    Piecewise Aggregate Approximation (PAA) signal compression method :py:func:`tsc.utils.compression.compress_paa()`.
    Spaces out the windowed results based on the ``window_size`` used to compute the PAA output, and linearly
    interpolates in between. On the edges of the signal, the function extrapolates out to the original edge start and
    finish.
    This is useful when feeding a reconstructed signal into a machine learning pipeline expecting a specifically-sized
    input.

    :param signal: 1d signal to compress and reconstruct.
    :param original_signal_size: size of original signal before compression.
    :param window_size: size of window to use to partition the signal.
    :return: 1D array of compressed and reconstructed ``signal`` array.
    :rtype: ``np.ndarray``.
    """

    # note the windows are not a perfect partition
    #   if the window size isn't perfectly divisible by the original signal size
    start_window, stop_window, _ = segmentation(ts_size=original_signal_size,
                                                window_size=window_size, overlapping=True)
    # the stop windows come out for list indexing (e.g. "up to but not including")
    #  need to subtract 1 to make the mean the actual meaningful location of the paa index value
    windowed_indices = np.c_[start_window, stop_window - 1].mean(axis=1)

    return reconstruct_tsc(signal=np.c_[windowed_indices, signal], x_values=np.arange(original_signal_size))[:, 1]


def reconstruct_random(signal: np.ndarray, x_values: list = None) -> np.ndarray:
    """
    Reconstructs the compression results as returned from :py:func:`tsc.utils.compression.compress_random` back to its
    original size, performing a linear interpolation between the dropped time values.
    This is useful when feeding a reconstructed signal into a machine learning pipeline expecting a
    specifically-sized input.

    :param signal: ``(k, 2)`` array of the signal to reconstruct, where the first column
        represents the times / domain / x points of the signal and the second column represents the
        scalars / range / y points corresponding to each time.
    :param x_values: values for the final time / domain / x points of the signal for which to reconstruct. Default
        ``None`` uses the ``int`` values between ``signal[0, 0]`` and ``signal[-1, 0]``.
    :return: 2D array of compressed and reconstructed ``signal`` array, where the first column
        represents the times / domain / x points of the signal and the second column represents the
        scalars / range / y points corresponding to each time.
    :rtype: ``np.ndarray``.
    """
    # random reconstruction also requires keeping the endpoints
    #   so the linear reconstruction is algorithmically equivalent to TSC reconstruction
    return reconstruct_tsc(signal=signal, x_values=x_values)
