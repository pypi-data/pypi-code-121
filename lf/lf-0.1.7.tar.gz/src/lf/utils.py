""" Provides the repeatedNans, findNans, get_azimuth, rot_az, tx_rx_midpoint,
and solar_max_time functions

repeatedNans determines the lengths of consecutive nan values in an array.
findNans provides the start and end locations of nans in an array.
get_azimuth determines the angle between a receiver and transmitter
rot_az calculates the phi and r components of magnetic field based on azimuth angle
tx_rx_midpoint calculate the midpoint between a receiver and transmitter
solar_max_time determines the time at which solar maximum occurs for a given lat, lon
"""

from datetime import datetime, timedelta, timezone

import numpy as np
import pysolar.solar
from geographiclib.geodesic import Geodesic

import lf.txrx as txrx

geod = Geodesic.WGS84


def repeatedNans(array):
    """ Determine the number of repeated nans in a row

    Parameters
    ----------
    array : np.array
        Array containing nan "strings"

    Returns
    -------
    np.array or None
        Array of the lengths of each nan "string"

    """
    idx = findNans(array)
    if idx is not None:
        return idx[1::2] - idx[::2]
    return None


def findNans(array):
    """ Find the start and stop location of nans

    Parameters
    ----------
    array : np.array
        array of data to find nans start/stop locations

    Returns
    -------
    np.array or None
        array of the start and stop locations of each nan "string" or None

    """
    mask = np.concatenate(([False], np.isnan(array), [False]))
    if not mask.any():
        return None
    return np.nonzero(mask[1:] != mask[:-1])[0]


def get_azimuth(rx, tx):
    """ Get the azimuth angle between the receiver and transmitter

    Parameters
    ----------
    rx : str
        Receiver abbreviation
    tx : str
        Transmitter call sign

    Returns
    -------
    float
        Azimuth angle

    """
    line = geod.InverseLine(
        txrx.rx_dict[rx][0],
        txrx.rx_dict[rx][1],
        txrx.tx_dict[tx][0],
        txrx.tx_dict[tx][1],
    )
    return line.azi1


def rot_az(angle_deg):
    """ Determine rotation factors for rotating azimuth

    Parameters
    ----------
    angle_deg : float
        Degree to rotate by

    Returns
    -------
    np.array
        New amplitude and phase components

    """
    ang = np.deg2rad(angle_deg)
    return np.array([[-np.sin(ang), np.cos(ang)], [-np.cos(ang), -np.sin(ang)]])


def rot_tilt(angle_deg):
    """ Determine rotation factors for rotating between radial/azimuth coordinates to polarized elliptical coordinates

    Parameters
    ----------
    angle_deg : float
        Degree to rotate by

    Returns
    -------
    np.array
        New amplitude and phase components

    """
    ang = np.deg2rad(angle_deg)
    return np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])


def tx_rx_midpoint(tx, rx):
    """ Compute the location of the midpoint between transmitter and receiver

    Parameters
    ----------
    tx : str
        Transmitter of interest
    rx : str
        Receiver of interest

    Returns
    -------
    float, float
        latitude, longitude of midpoint

    """
    # Lookup table for transmitter and receiver lat long
    tx_lat, tx_lon = txrx.tx_dict[tx][0:2]
    rx_lat, rx_lon = txrx.rx_dict[rx][0:2]

    line = geod.InverseLine(tx_lat, tx_lon, rx_lat, rx_lon)
    distance = line.s13
    az = line.azi1
    g = geod.Direct(tx_lat, tx_lon, az, distance / 2)
    return g["lat2"], g["lon2"]


def solar_max_time(lat, lon, day=None, dates=None):
    """ Calculate when the sun is most abovehead

    Parameters
    ----------
    lat : float
        Latitude of interest
    lon : float
        Longitude of interest
    day : datetime, optional
        Day of interest
    dates : list, optional
        List of times to compare

    Returns
    -------
    datetime
        Time of maximal sun overheadness

    """
    if not dates:
        assert isinstance(day, datetime)
        day = day.replace(tzinfo=timezone.utc)
        assert day.second == 0
        assert day.minute == 0
        assert day.hour == 0
        dates = [day + timedelta(minutes=x) for x in range(24 * 60)]

    altitudes = [pysolar.solar.get_altitude(lat, lon, date) for date in dates]
    return dates[np.argmax(altitudes)]
