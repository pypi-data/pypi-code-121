"""Script to put any function that creates correctly formatted dates."""


import datetime as dt
from itertools import cycle
from typing import List, Tuple, Union

import cftime
import numpy as np

from volcano_cooking.modules import create


def single_date_and_emission(
    init_year: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Create a single volcano three years after `init_year`.

    Parameters
    ----------
    init_year: int
        The first year dates should appear in

    Returns
    -------
    yoes: np.ndarray
        Array of length 'size' with the year of a date
    moes: np.ndarray
        Array of length 'size' with the month of a date
    does: np.ndarray
        Array of length 'size' with the day of a date
    veis: np.ndarray
        Array of length 'size' with the VEI as a 1D numpy array
    """
    yoes = np.array([init_year - 1, init_year + 2, init_year + 100], dtype=np.int16)
    moes = np.array([1, 1, 1], dtype=np.int8)
    does = np.array([15, 15, 15], dtype=np.int8)
    tes = np.array([1, 400, 1], dtype=np.float32)
    return yoes, moes, does, tes


def random_dates(
    size: int, init_year: Union[float, str]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create random dates and place them in order.

    The randomness do not follow a specific model. This is the simplest case where we just
    use the 'randint' function from 'numpy'.

    Parameters
    ----------
    size: int
        The total number of dates that should be made.
    init_year: float, str
        The first year dates should appear in

    Returns
    -------
    yoes: np.ndarray
        Array of length 'size' with the year of a date
    moes: np.ndarray
        Array of length 'size' with the month of a date
    does: np.ndarray
        Array of length 'size' with the day of a date

    Raises
    ------
    ValueError
        If `size` is non-positive.
    """
    if size < 1:
        raise ValueError(f"{size} = , but must be > 0.")
    yoes = np.cumsum(np.random.randint(0, high=2, size=size)).astype(np.int16) + int(
        init_year
    )
    moes = np.random.randint(1, high=12, size=size, dtype=np.int8)
    does = np.random.randint(1, high=28, size=size, dtype=np.int8)
    # Make sure dates are increasing!
    # idx = list of arrays of indexes pointing to the same year
    idxs = [np.where(yoes == i)[0] for i in np.unique(yoes)]
    # sort months with indexes
    # sort days with indexes
    for idx in idxs:
        moes[idx] = np.sort(moes[idx])
        does[idx] = np.sort(does[idx])

    return yoes, moes, does


def regular_intervals():
    """Create dates with regular intervals.

    This function creates dates with regular intervals and a pre-defined magnitude as
    VEI.

    Returns
    -------
    yoes: np.ndarray
        Array of length 'size' with the year of a date
    moes: np.ndarray
        Array of length 'size' with the month of a date
    does: np.ndarray
        Array of length 'size' with the day of a date
    veis: np.ndarray
        Array of length 'size' with the VEI
    """
    year_sep = 2
    init_year = 1850
    month = 3
    day = 15
    size = 100
    te = cycle([5, 1000, 40, 200])
    yoes = np.zeros(size, dtype=np.int16) + init_year
    moes = np.zeros(size, dtype=np.int8) + month
    does = np.zeros(size, dtype=np.int8) + day
    tes = np.ones(size, dtype=np.float32)
    for i in range(size):
        yoes[i] += i * year_sep
        tes[i] = next(te)
    return yoes, moes, does, tes


def fpp_dates_and_emissions(
    size: int, init_year: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Create random ordered dates and total emissions.

    Data is created from an FPP process, specifically the arrival time and amplitude is
    used to set dates and total emissions.

    Parameters
    ----------
    size: int
        The total number of dates that should be made.
    init_year: int
        The first year dates should appear in

    Returns
    -------
    yoes: np.ndarray
        Array of length 'size' with the year of a date
    moes: np.ndarray
        Array of length 'size' with the month of a date
    does: np.ndarray
        Array of length 'size' with the day of a date
    tes:
        Array of length 'size' with the Total_Emission as a 1D numpy array
    """
    f = create.StdFrc(fs=12, total_pulses=size)
    while True:
        ta, amp = f.get_frc()
        # Can't have years beyond 9999
        if int(ta[-1]) + init_year > 9999:
            prev_size = int(ta[-1]) + init_year
            mask = np.argwhere(ta + init_year < 9999)
            ta = ta[mask].flatten()
            amp = amp[mask].flatten()
            size = len(amp)
            print(
                "Can't create dates for years beyond 9999. Keep this in mind when "
                + f"setting `init_year` and `size`. Size: {prev_size} -> {size}."
            )
        # Go from float to YYYY-MM-DD
        dates: List[cftime.datetime] = []
        dates_ap = dates.append
        for n in ta:
            result = cftime.datetime(
                int(n) + init_year, 1, 1, calendar="noleap"
            ) + dt.timedelta(days=(n % 1) * 365)
            dates_ap(result)
        # Dates should be unique
        if not any(np.diff(dates) == dt.timedelta(days=0)):
            break
    yoes_l: List[int] = []
    yoes_ap = yoes_l.append
    moes_l: List[int] = []
    moes_ap = moes_l.append
    does_l: List[int] = []
    does_ap = does_l.append
    for d in dates:
        yoes_ap(d.year)
        moes_ap(d.month)
        does_ap(d.day)
    yoes = np.array(yoes_l, dtype=np.int16)
    moes = np.array(moes_l, dtype=np.int8)
    does = np.array(does_l, dtype=np.int8)
    del yoes_l
    del moes_l
    del does_l
    tes = np.array(amp, dtype=np.float32)
    return yoes, moes, does, tes
