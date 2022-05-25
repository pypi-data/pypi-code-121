#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 13:51:59 2022

@author: frostig
"""
import astropy.time
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz
import numpy as np
import pandas as pd
import pytz
from datetime import datetime
import psycopg
import getpass
import logging
from wintertoo.data import program_db_host, palomar_loc, palomar_observer, camera_field_size

logger = logging.getLogger(__name__)


# get alt and az of observations
# in decimal degrees
def get_alt_az(times, ra, dec):
    loc = SkyCoord(ra=ra, dec=dec, frame='icrs')
    time = Time(times, format='mjd')
    altaz = loc.transform_to(AltAz(obstime=time, location=palomar_loc))
    degs = SkyCoord(altaz.az, altaz.alt, frame='icrs')
    # print('altaz'  , altaz)
    alt_array = degs.dec.degree
    az_array = degs.ra.degree

    return (alt_array, az_array)


# what is up (above altitude 20 deg) in a given night?
# date in MJD (median Julian Date), e.g. 59480 (Sept 23)
# ra (right ascension) in hours, minutes, seconds, e.g. '+19h50m41s'
# dec (declination) in hours, minutes, seconds, e.g. '+08d50m58s'
def up_tonight(
        time: astropy.time.Time,
        ra,
        dec
):
    loc = SkyCoord(ra=ra, dec=dec, frame='icrs')
    time = Time(time, format='mjd')
    sun_rise = palomar_observer.sun_rise_time(time, which="previous")
    sun_set = palomar_observer.sun_set_time(time, which="next")
    night = (sun_set.jd - sun_rise.jd)
    if night >= 1:
        # if next day, subtract a day
        dt = np.linspace(sun_set.jd, sun_set.jd + (night - 1), 100)
    else:
        dt = np.linspace(sun_set.jd, sun_set.jd + (night), 100)

    altaz = loc.transform_to(AltAz(obstime=Time(dt, format='jd'), location=palomar_loc))
    d = {'time': dt, 'alt': altaz.alt}
    df = pd.DataFrame(data=d)
    df = df[df['alt'] >= 20]  # can change limiting altitude here
    try:
        time_up = df['time'].iloc[-1] - df['time'].iloc[0]
    except:
        time_up = 0

    if time_up > 0:
        start = Time(df['time'].iloc[0], format='jd').isot
        end = Time(df['time'].iloc[-1], format='jd').isot
        is_available = 'Object is up between UTC ' + str(start) + ' and ' + str(end)
        avail_bool = True
    else:
        is_available = 'Object is not up'
        avail_bool = False

    return (avail_bool, is_available)


### backend 
def rad_to_deg(x):
    return x * 180 / np.pi




git_path = '../daily_summer_scheduler/data/'

field_filename = git_path + 'SUMMER_fields.txt'


def get_tonight(data):
    if data['time_units'] == 'mjd':
        tonight = np.floor(float(data['start_time']))
        start_time = Time(float(data['start_time']), format='mjd')
        stop_time = Time(float(data['stop_time']), format='mjd')

    else:
        pacific = pytz.timezone("PST8PDT")
        # convert iso string to datetime object to astropy time object
        dt = datetime.datetime.fromisoformat(str(data['start_time']))
        dt2 = pacific.localize(
            datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond))
        dt3 = dt2.astimezone(pytz.utc)
        start_time = Time(dt3, scale='utc')

        dt = datetime.datetime.fromisoformat(str(data['stop_time']))
        dt2 = pacific.localize(
            datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond))
        dt3 = dt2.astimezone(pytz.utc)
        stop_time = Time(dt3, scale='utc')

        tonight = np.floor(start_time.mjd)

    return tonight


def get_start_stop_times(data):
    if data['time_units'] == 'mjd':
        start_time = Time(float(data['start_time']), format='mjd')
        stop_time = Time(float(data['stop_time']), format='mjd')

    else:
        pacific = pytz.timezone("PST8PDT")
        # convert iso string to datetime object to astropy time object
        dt = datetime.datetime.fromisoformat(str(data['start_time']))
        dt2 = pacific.localize(
            datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond))
        dt3 = dt2.astimezone(pytz.utc)
        start_time = Time(dt3, scale='utc')

        dt = datetime.datetime.fromisoformat(str(data['stop_time']))
        dt2 = pacific.localize(
            datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond))
        dt3 = dt2.astimezone(pytz.utc)
        stop_time = Time(dt3, scale='utc')

    return start_time, stop_time


def get_field_ids(ras, decs, units="degrees"):
    field_list = []

    lists = [ras, decs]
    if len(set(map(len, lists))) not in (0, 1):
        raise ValueError('RA and Dec lists are not the same length')

    for ra, dec in zip(ras, decs):
        summer_fields = pd.read_csv(field_filename,
                                    names=['field_id', 'ra', 'dec', 'ebv', 'l', 'b',
                                           'ecliptic_lon', 'ecliptic_lat', 'number'],
                                    sep='\s+', usecols=['field_id', 'ra', 'dec', 'l', 'b',
                                                        'ecliptic_lon', 'ecliptic_lat'], index_col='field_id',
                                    skiprows=1)
        ra = float(ra)
        dec = float(dec)
        if units == "radians":
            ra_degs = rad_to_deg(ra)
            dec_degs = rad_to_deg(dec)
        elif units == "degrees":
            ra_degs = ra
            dec_degs = dec
        else:
            raise ValueError(f"Units '{units}' not recognised")

        print(ra, dec)
        # sort dec
        dec_sort = summer_fields.iloc[((summer_fields['dec'] - dec_degs).abs() <= camera_field_size).values]

        # sort ra
        ra_sort = dec_sort.iloc[((dec_sort['ra'] - ra_degs).abs() <= camera_field_size).values]

        field_num = ra_sort.index[0]
        field_list.append(int(field_num))

    return field_list


def get_program_details(
        program_name: str,
        user: str = None,
        password: str = None,
        host: str = program_db_host
) -> pd.DataFrame:

    if user is None:
        user = input("Enter user: ")

    if password is None:
        password = getpass.getpass(f"Enter password for user {user}: ")

    with psycopg.connect(f"dbname='commissioning' user={user} password={password} host={host}") as conn:
        command = f'''SELECT * FROM programs WHERE programs.progname = '{program_name}';'''
        with conn.execute(command) as cursor:
            colnames = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            data = pd.DataFrame(data, columns=colnames)

    return data
