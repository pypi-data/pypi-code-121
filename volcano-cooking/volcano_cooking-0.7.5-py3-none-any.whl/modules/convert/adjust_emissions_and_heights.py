"""Adjust emissions and emission heights to go into the CESM2.

Too much aerosols in a column can trigger a warning saying that the `Aerosol optical depth
is unreasonably high in this layer.` We therefore restrict this, as well as correcting for
the injections heights, making sure they are within the range of the model layers.

Note
----
Modified from script provided by Herman Fæhn Fuglestvedt and using
http://svn.code.sf.net/p/codescripts/code/trunk/ncl/emission/createVolcEruptV3.ncl
"""
import os
from typing import Tuple

import numpy as np
import xarray as xr


def adjust_altitude_range(
    miihs: np.ndarray, mxihs: np.ndarray, tes: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Adjust altitude range to within the layers of CESM2.

    Parameters
    ----------
    miihs: np.ndarray
        Minimum injection heights
    mxihs: np.ndarray
        Maximum injection heights
    tes: np.ndarray
        Total emissions

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Adjusted minimum and maximum injection heights

    Note
    ----
    Python implementation of the correction from:
    http://svn.code.sf.net/p/codescripts/code/trunk/ncl/emission/createVolcEruptV3.ncl
    """
    threshold = 3.5  # Tg
    idx = (tes > threshold) & (mxihs > 20)
    mxihs[idx] = 20
    # If some of the lower boundaries at `idx` are higher than 18, we set them to 18.
    miihs[idx & (miihs > 18)] = 18
    return miihs, mxihs


def adjust_emissions(
    miihs: np.ndarray,
    mxihs: np.ndarray,
    tes: np.ndarray,
    e_lons: np.ndarray,
    e_lats: np.ndarray,
) -> np.ndarray:
    """Calculate emissions that are accepted by the CESM2.

    Too much aerosols in a column can trigger a warning saying that the `Aerosol optical
    depth is unreasonably high in this layer`. We therefore restrict this, should be on
    the order of about `1e10`.

    Parameters
    ----------
    miihs: np.ndarray
        Minimum injection heights
    mxihs: np.ndarray
        Maximum injection heights
    tes: np.ndarray
        Total emissions
    e_lons: np.ndarray
        Longitude of the eruption
    e_lats: np.ndarray
        Latitude of the eruption

    Returns
    -------
    np.ndarray
        The total column emission

    Note
    ----
    Modified from script provided by Herman Fæhn Fuglestvedt and according to
    http://svn.code.sf.net/p/codescripts/code/trunk/ncl/emission/createVolcEruptV3.ncl

    Raises
    ------
    FileNotFoundError
        If the coordinates file cannot be found.
    """
    file = os.path.join(
        "data",
        "originals",
        "fv_1.9x2.5_L30",
    )
    if not os.path.exists(f"{file}.nc"):
        raise FileNotFoundError(f"{file} not found. Consult README on how to download.")
    mass_threshold = 15
    idx = tes > mass_threshold
    mass_factor = 1 / 1.8  # scaling factor for large eruptions
    tes[idx] *= mass_factor

    duration = 21600  # 6 hours in seconds
    avogadros_number = 6.022140857e23  # Avogadro's constant in "mol^{-1}"
    d_earth = 12742e3  # in "m"
    s_earth = np.pi * d_earth ** 2
    # dalt = 1e3
    dalt = mxihs * 1e5 - miihs * 1e5  # Emission depth in cm
    m3_to_cm3 = 1.0e6
    kg2g = 1000
    m_mass, fraction = (64.06, 1.0)

    grid = xr.open_dataset(os.path.join("data", "originals", "fv_1.9x2.5_L30.nc"))
    gw = grid["gw"]  # Latitude/Gauss weights
    nLon = len(grid["lon"])
    # nLat = len(grid["lat"])
    lat_data = grid["lat"]
    column_area = s_earth / nLon * gw / np.sum(gw)  # in "m"
    idx = (np.abs(e_lats - lat_data)).argmin()
    area = column_area[idx] * len(e_lons)
    volume = area.data * dalt  # volume of one level
    v_cm3 = volume * m3_to_cm3  # Volume in cm3
    # tot_molecules = tes * kg2g / m_mass * avogadros_number  # "imass" is in "kg"
    # emis = tot_molecules / (v_cm3 * duration)
    # total = ((v_cm3 * emis * duration) / avogadros_number * m_mass) / kg2g * fraction
    # print(total)

    emis = tes / area.data / duration
    column_emission = emis * kg2g / m_mass * avogadros_number  # "imass" is in "kg"
    # emis_rate = column_emission / dalt
    _ = ((v_cm3 * emis * duration) / avogadros_number * m_mass) / kg2g * fraction
    # print(total)

    # stratvolc =

    return column_emission
