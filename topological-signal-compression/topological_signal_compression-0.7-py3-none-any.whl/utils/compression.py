# Gary Koplik
# gary<dot>koplik<at>geomdata<dot>com
# April, 2020. Last modified March, 2022.
# compression.py

"""
Counterfactual signal compression methods. This module handles *only* compression, *not* reconstruction.
For more on reconstruction, see the :py:mod:`tsc.utils.reconstruction` module.
"""

import numpy as np
import os
from pyts.approximation import DiscreteFourierTransform, PiecewiseAggregateApproximation
from scipy.io.wavfile import write
from tsc.utils.helper_functions import min_max_normalize


def compress_dft(signal: np.ndarray, percent_compressed: float) -> np.ndarray:
    """
    Run Discrete Fourier Transform compression on a signal, returning Fourier coefficients representing the signal.
    (This is useful when feeding a reconstructed signal into a machine learning pipeline expecting a specifically-sized
    input.)

    :param signal: 1d signal to compress and reconstruct.
    :param percent_compressed: percent (e.g. in [0, 100]) that the resulting output should be compressed on disk
        (e.g. ``percent_compressed=20`` should be 20% compressed or 80% the size of the original signal).
    :return: 1D array of compressed and reconstructed ``signal`` array.
    :rtype: ``np.ndarray``.
    """

    # NOTE: remember compression here will
    # 1. be run as percent of points SAVED not compressed
    # 2. be run as a decimal in (0, 1), not a percentage
    fraction_compressed = 1 - percent_compressed / 100
    arr = signal.reshape(1, -1).astype(np.float32)
    dft = DiscreteFourierTransform(n_coefs=fraction_compressed, norm_mean=False, norm_std=False)
    compressed = dft.fit_transform(arr).astype(np.float32).flatten()
    return compressed


def compress_opus(signal: np.ndarray, wav_path: str, bitrate: int, log_file: str, sampling_rate: int = 8000) -> str:
    """
    Run Opus compression on a 1d signal ``signal``. Will save a file in the same place and with the same
    name as ``wav_path``, but with a ``.opus`` file type instead.

    .. note::
        This requires an installation of `opus-tools <https://anaconda.org/conda-forge/opus-tools>`_ and
        `ffmpeg <https://anaconda.org/conda-forge/ffmpeg>`_. The ``topological-signal-compression`` package
        only maintains functionality for the installation of these packages through the ``conda install`` framework.

        There are other means of installing the needed Opus software for which we offer no guarantees, but one should
        only need to be able to run an ``opusenc`` call in a terminal.

        Lastly, this will likely only work for Unix machines. If it becomes relevant to support running this code
        on Windows machines, we will tackle that need as it comes up.

    :param signal: 1d signal to compress.
    :param wav_path: file path to save ``signal`` as ``.wav`` file before we can run Opus compression.
    :param bitrate: bitrate compression to use. Values should in a range of roughly 8 to 190, which corresponds to
        O(90%) and O(10%) compression, respectively.
    :param log_file: file path to ``tee`` append all stderr and stdout to disk when running opus call through bash.
    :param sampling_rate: sampling rate (in Hz) of the signal being compressed.
    :return: file path of saved ``.opus`` file.
    :rtype: ``str``.
    """

    # run ogg on normalized signal
    normalized_arr = min_max_normalize(arr=signal)
    write(wav_path, rate=sampling_rate, data=normalized_arr)

    # generate unique file name to save to disk
    opus_filename = os.path.join(os.path.dirname(wav_path),
                                 f"{os.path.basename(wav_path).split('.')[0]}.opus")
    # run opus compression on linux terminal through python, requires install of ``opus-tools``
    os.system(
        f"opusenc --quiet --bitrate {bitrate} {wav_path} {opus_filename} 2>&1 | tee -a {log_file} >/dev/null"
    )

    return opus_filename


def compress_paa(signal: np.ndarray, window_size: int) -> np.ndarray:
    """
    Run Piecewise Aggregate Approximation (PAA) compression on a signal.

    :param signal: 1d signal to compress and reconstruct.
    :param window_size: size of window to use to partition the signal.
    :return: 1D array of compressed ``signal`` array.
    :rtype: ``np.ndarray``.
    """
    arr = np.expand_dims(signal, 0).astype(np.float32)
    transformer = PiecewiseAggregateApproximation(window_size=window_size)
    paa_output = transformer.transform(arr).astype(np.float32).flatten()
    return paa_output


def compress_random(signal: np.ndarray, num_indices_to_keep: int or float = "all",
                    random_seed: int or None = None) -> np.ndarray:
    """
    Creates compression based on taking random draws (without replacement) of ``num_indices_to_keep`` points.

    To maintain spanning the same domain of the signal, the edge values will always be the first two values chosen.
    When specifying ``num_indices_to_keep = n``, the function will still return no more than ``n`` values.

    :param signal: ``(n, 2)`` array where the first column represents the times / domain / x points of the signal
        and the second column represents the scalars / range / y points corresponding to each time.
    :param num_indices_to_keep: number of points to keep from signal when reconstructing the signal.
        Can also offer the string "all" here for a trivial reconstruction using the full signal.
        Must specify an integer greater than 2 (will always return at least the edge values). Finally, can also offer
        a float between (0, 1) to return a percentage of values.
    :param random_seed: sets random seed to specified value (default ``None`` sets no random seed).
    :return: ``(k, 2)`` array (k <= n) representing the reconstructed signal where the first column represents the
        times / domain / x points of the signal and the second column represents the scalars / range / y points
        corresponding to each time.
    :rtype: ``np.ndarray``.
    """

    # set seed if specified
    if random_seed is not None:
        np.random.seed(random_seed)

    if num_indices_to_keep != "all":
        assert num_indices_to_keep >= 2 or 0 < num_indices_to_keep < 1, \
            "`num_indices_to_keep` must be >=2 since we always at least return the edge values\n" + \
            "or be in (0, 1) representing returning a reconstruction using only a percentage of the values"

    if num_indices_to_keep == "all":
        return signal

    else:
        # start with requiring edges be included
        indices = [0, signal.shape[0] - 1]

        # convert fraction to number of points if necessary
        if 0 < num_indices_to_keep < 1:
            num_indices_to_keep = int(signal.shape[0] * num_indices_to_keep)

        # add edge indices plus a random subset
        indices += list(np.random.choice(np.arange(1, signal.shape[0] - 1),
                                         size=num_indices_to_keep - 2,
                                         replace=False))
        return signal[sorted(indices), :]
