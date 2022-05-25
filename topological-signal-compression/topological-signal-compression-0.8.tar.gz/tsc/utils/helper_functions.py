# Gary Koplik, Sam Voisin
# gary<dot>koplik<at>geomdata<dot>com
# August, 2020. Last modified March, 2022
# helper_functions.py

"""
Helper utility functions for various compression and reconstruction capabilities.
"""

import numpy as np
from pydub import AudioSegment


def min_max_normalize(arr: np.ndarray) -> np.ndarray:
    """
    Convert ``numpy`` array ``arr`` to a form suitable for encoding as ``wav`` file. Then min-max normalize the array
    (e.g. make signal values span [0, 1]) and change ``dtype`` to 32-bit floating point.

    :param arr: 1D ``numpy`` array.
    :return: 1D array.
    :rtype: ``np.ndarray``.
    """
    res = (arr - arr.min()) / (arr.max() - arr.min())
    res = res.astype(np.float32)
    return res


def pydub_to_numpy(audiosegment: AudioSegment) -> np.ndarray:
    """
    Turn a multichannel ``pydub.AudioSegment`` instance to a ``numpy.ndarray`` with only a single channel of sound.

    :param audiosegment: ``pydub.AudioSegment`` instance to convert.
    :return: 1d array of signal with type ``float32`` for consistency with other compression schemes.
    :rtype: ``np.ndarray``.
    """

    # get numpy array of sound
    samples = np.array(audiosegment.get_array_of_samples()).reshape(audiosegment.channels, -1, order="F")
    # convert to single channel audio array
    samples = samples.sum(axis=0) / audiosegment.channels
    return samples.astype(np.float32)
