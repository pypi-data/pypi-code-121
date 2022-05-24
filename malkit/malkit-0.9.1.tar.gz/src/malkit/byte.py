import functools
import math
from typing import Any, Iterable, Optional, Tuple

import numpy as np

from ._parallel import reduce_parallel
from ._typing import FilePath

__all__ = [
    "extract_byte_hist",
    "extract_byte_hist_parallel",
    "extract_byte_entropy_hist",
    "extract_byte_entropy_hist_parallel",
]


def get_byte_hist(buffer: bytes) -> np.ndarray:
    """Get byte histogram."""

    byte_seq = np.frombuffer(buffer, dtype=np.uint8)
    return np.bincount(byte_seq, minlength=256)


def extract_byte_hist(binary_file: FilePath) -> np.ndarray:
    """Extract byte histogram."""

    with open(binary_file, "rb") as f:
        buffer = f.read()
    return get_byte_hist(buffer)


def extract_byte_hist_parallel(
    binary_files: Iterable[FilePath], *, n_jobs: Optional[int] = None, **kwargs: Any
) -> np.ndarray:
    """Extract byte histogram in parallel."""

    return reduce_parallel(extract_byte_hist, binary_files, n_jobs=n_jobs, **kwargs)


def _get_entropy_and_byte_hist(window: np.ndarray) -> Tuple[np.float64, np.ndarray]:
    byte_hist = np.bincount(window, minlength=256)
    prob = byte_hist / len(window)
    mask = prob > 0
    entropy = -np.sum(prob * np.log2(prob, where=mask))
    return entropy, byte_hist


def get_byte_entropy_hist(buffer: bytes, *, window_size: int = 1024, step_size: int = 256) -> np.ndarray:
    """Get byte entropy histogram.

    References:
        - J. Saxe and K. Berlin. 2015.
          Deep neural network based malware detection using two dimensional binary program features.
          https://doi.org/10.1109/MALWARE.2015.7413680
    """

    byte_seq = np.frombuffer(buffer, dtype=np.uint8)
    result = np.zeros((16, 256), dtype=np.int64)
    for window in np.lib.stride_tricks.sliding_window_view(byte_seq, window_size)[::step_size]:
        entropy, byte_hist = _get_entropy_and_byte_hist(window)
        idx = min(math.floor(entropy * 2), 15)
        result[idx] += byte_hist
    return result.reshape((16, 16, 16)).sum(-1).reshape(256)


def extract_byte_entropy_hist(binary_file: FilePath, *, window_size: int = 1024, step_size: int = 256) -> np.ndarray:
    """Extract byte entropy histogram."""

    with open(binary_file, "rb") as f:
        buffer = f.read()
    return get_byte_entropy_hist(buffer, window_size=window_size, step_size=step_size)


def extract_byte_entropy_hist_parallel(
    binary_files: Iterable[FilePath],
    *,
    window_size: int = 1024,
    step_size: int = 256,
    n_jobs: Optional[int] = None,
    **kwargs: Any,
) -> np.ndarray:
    """Extract byte entropy histogram in parallel."""

    function = functools.partial(extract_byte_entropy_hist, window_size=window_size, step_size=step_size)
    return reduce_parallel(function, binary_files, n_jobs=n_jobs, **kwargs)
