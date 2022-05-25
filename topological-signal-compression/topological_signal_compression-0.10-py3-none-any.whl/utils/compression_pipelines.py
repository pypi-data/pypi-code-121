# Gary Koplik
# gary<dot>koplik<at>geomdata<dot>com
# August, 2020. Last modified March, 2022.
# compression_pipelines.py

"""
Wrapper methods to do *both* compression and reconstruction for all supported counterfactual compression methodologies.
Runs on 1d ``numpy.ndarray`` inputs.

To find the methods that do *just* compression *or* reconstruction, see the :py:mod:`tsc.utils.compression` and
:py:mod:`tsc.utils.reconstruction` modules, respectively.

Note, the standalone compression and reconstruction methods, and the pipeline for Topological Signal compression are
available with :py:func:`~tsc.__init__.compress_tsc()`, :py:func:`~tsc.__init__.reconstruct_tsc()`, and
:py:func:`~tsc.__init__.tsc_pipeline()` respectively.
"""


import numpy as np
from tsc.utils.compression import compress_dft, compress_opus, compress_paa, compress_random
from tsc.utils.reconstruction import reconstruct_dft, reconstruct_opus, reconstruct_paa, reconstruct_random


def dft_pipeline(signal: np.ndarray, percent_compressed: float) -> np.ndarray:
    """
    Run Discrete Fourier Transform compression on a signal and reconstruct with linear interpolation.
    Reconstructs the signal to be back to its original size.

    :param signal: 1d signal to compress and reconstruct.
    :param percent_compressed: percent (e.g. in [0, 100]) that the resulting output should be compressed on disk
        (e.g. ``percent_compressed=20`` should be 20% compressed or 80% the size of the original signal).
    :return: 1D array of compressed and reconstructed ``signal`` array.
    :rtype: ``np.ndarray``.
    """

    # NOTE: remember compression here will
    # 1. be run as percent of points SAVED not compressed
    # 2. be run as a decimal in (0, 1), not a percentage
    length = signal.size
    compressed = compress_dft(signal=signal, percent_compressed=percent_compressed)
    output = reconstruct_dft(compressed, length)
    return output


def opus_pipeline(signal: np.ndarray, wav_path: str, bitrate: int,
                  log_file: str, sampling_rate: int = 8000) -> np.ndarray:
    """
    Run Opus compression on a 1d signal ``signal`` and reconstruct. Will save a file in the same place and with the same
    name as ``wav_path``, but with a ``.opus`` file type instead.
    Reconstructs the signal to be back to its original size.

    .. note::
        This requires an installation of `opus-tools <https://anaconda.org/conda-forge/opus-tools>`_ and
        `ffmpeg <https://anaconda.org/conda-forge/ffmpeg>`_. The ``topological-signal-compression`` package
        only maintains functionality for the installation of these packages through the ``conda install`` framework.

        There are other means of installing the needed Opus software for which we offer no guarantees, but one should
        only need to be able to run an ``opusenc`` call in a terminal.

        Lastly, this will likely only work for Unix machines. If it becomes relevant to support running this code
        on Windows machines, we will tackle that need as it comes up.

    :param signal: 1d signal to compress and reconstruct.
    :param wav_path: file path to save ``signal`` as ``.wav`` file before we can run Opus compression.
    :param bitrate: bitrate compression to use. Values should be in a range of roughly 8 to 190, which corresponds to
        O(90%) and O(10%) compression, respectively, for compressing the Free-Spoken Digit Dataset (FSDD). Compression
        percentages will vary depending on ``signal`` input.
    :param log_file: file path to ``tee`` append all stderr and stdout to disk when running opus call through bash.
    :param sampling_rate: sampling rate (in Hz) of the signal being compressed.
    :return: 1D array of compressed and reconstructed signal.
    :rtype: ``np.ndarray``.
    """

    # run opus on normalized signal
    opus_filename = compress_opus(signal=signal, wav_path=wav_path, bitrate=bitrate,
                                  log_file=log_file, sampling_rate=sampling_rate)
    return reconstruct_opus(filepath=opus_filename, sampling_rate=sampling_rate)


def paa_pipeline(signal: np.ndarray, window_size: int) -> np.ndarray:
    """
    Run Piecewise Aggregate Approximation (PAA) compression on a signal and reconstruct with linear interpolation.
    Reconstructs the signal to be back to its original size.

    :param signal: 1d signal to compress and reconstruct.
    :param window_size: size of window to use to partition the signal.
    :return: 1D array of compressed and reconstructed ``signal`` array.
    :rtype: ``np.ndarray``.
    """

    paa_output = compress_paa(signal=signal, window_size=window_size)
    output = reconstruct_paa(paa_output, original_signal_size=len(signal), window_size=window_size)
    return output


def random_pipeline(signal: np.ndarray, n_keep: int or float, random_seed: int = None) -> np.ndarray:
    """
    Perform random signal compression and reconstruction. Reconstructs the signal to be back to its original size with
    linear interpolation.

    :param signal: 1d signal to compress and reconstruct.
    :param n_keep: number of points to keep. If this is a fraction in (0, 1) it
        will be treated as a percentage of points to retain. If this is an
        integer >=2 it will be treated as the number of points to retain.
    :param random_seed: sets random seed so random reconstruction can be the same if drawn multiple times.
        Default ``None`` does a different random reconstruction each time called.
    :return: 1D array of compressed and reconstructed ``signal`` array.
    :rtype: ``np.ndarray``.
    """
    if n_keep >= signal.shape[0]:
        return signal
    n = signal.shape[0]
    random_output = compress_random(np.c_[np.arange(n), signal],
                                    num_indices_to_keep=n_keep,
                                    random_seed=random_seed)
    return reconstruct_random(random_output)[:, 1]
