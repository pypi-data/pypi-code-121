"""Script with functions that converts one variable to another.

The converting functions are made through trial and error by matching the synthetically
created variables with one real data set used in CESM2.
"""

from typing import Tuple

import numpy as np


def vei_to_totalemission(veis: np.ndarray) -> np.ndarray:
    """Convert from VEI to Total_Emission.

    Parameters
    ----------
    veis: np.ndarray
        The array of VEI that should be converted to Total_Emission

    Returns
    -------
    np.ndarray
        The resulting Total_Emission's array as a 1D numpy array

    Raises
    ------
    ValueError
        If the input is not an array of float32.
    """
    if veis.dtype != np.int8:
        raise ValueError(f"{veis.dtype} = . Need int8.")
    return 1e-2 * 3 ** (
        np.random.normal(0.1, 1.0, size=len(veis)).astype(np.float32) + veis
    )


def totalemission_to_vei(tes: np.ndarray) -> np.ndarray:
    """Convert from Total_Emission to VEI.

    All values in the VEI array are mapped to [0, 7].

    Parameters
    ----------
    tes: np.ndarray
        The array of Total_Emission that should be converted to VEI

    Returns
    -------
    np.ndarray
        The resulting VEI's array as a 1D numpy array

    Raises
    ------
    ZeroDivisionError
        If `tes` has non-positive values.
    """
    if any(tes <= 0):
        raise ZeroDivisionError(
            "Don't use total emission with zeros. We're doing a log."
        )
    base = 4
    veis = np.log(tes) / np.log(base)
    veis -= np.min(veis) + 0.2
    veis = veis.astype(np.int8) % 7

    return veis


def vei_to_injectionheights(veis: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Convert VEI to minimum and maximum injection heights.

    When we set the minimum and maximum injection heights we should make sure the minimum
    value really is less than the maximum value, hence the for loop at the end.  The
    variables 'scale_min' and 'scale_max' were adjusted based on the helper script
    'inspect_X-vs-Y.py'.

    Parameters
    ----------
    veis: np.ndarray
        The array of VEI that should be converted to Total_Emission

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        The resulting minimum and maximum injection heights as a 1D numpy arrays.
        The first element is the lower bound, second is upper bound.
    """
    scale_max = np.array([80 if v > 3 else 10 for v in veis])
    scale_min = np.array([20 if v > 3 else 1 for v in veis])
    mxihs = np.abs(
        np.random.normal(1, 2.0, size=len(veis)).astype(np.float32) * scale_max
    )
    miihs = np.abs(
        np.random.normal(1, 2.0, size=len(veis)).astype(np.float32) * scale_min
    )
    # Finally we make sure the lower bound is less than 30:
    idx_min = miihs > 30
    miihs[idx_min] = 18
    idx_max = mxihs > 30
    mxihs[idx_max] = 20

    for idx, (i, j) in enumerate(zip(miihs, mxihs)):
        miihs[idx] = min(i, j)
        mxihs[idx] = max(i, j)
    mxihs = mxihs.astype(np.float32)
    miihs = miihs.astype(np.float32)
    return miihs, mxihs
