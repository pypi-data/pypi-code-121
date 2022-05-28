#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 13:22:21 2021

@author: mike
"""
import os
import socket
import numpy as np
import zstandard as zstd
import pickle
import pandas as pd
import smtplib
import ssl
import requests
import orjson
from email.message import EmailMessage
from glob import glob
from datetime import date, datetime
import hashlib
import xarray as xr
# from blake3 import blake3
import zlib
from time import sleep
import uuid
import pathlib

############################################
### Parameters



############################################
### Functions


def path_date_parser(path, date_format=None):
    """

    """
    name1 = os.path.split(path)[1]
    date1 = pd.to_datetime(name1, format=date_format, exact=False, infer_datetime_format=True)

    return date1


def filter_data_paths(paths, date_format=None, from_date=None, to_date=None, return_dates=False):
    """

    """
    dates = pd.DataFrame([[p, path_date_parser(p, date_format=date_format)] for p in paths], columns=['path', 'date'])

    if isinstance(from_date, (str, pd.Timestamp, date, datetime)):
        dates = dates[dates['date'] >= pd.Timestamp(from_date)].copy()
    if isinstance(to_date, (str, pd.Timestamp, date, datetime)):
        dates = dates[dates['date'] <= pd.Timestamp(to_date)].copy()

    if not return_dates:
        dates = dates['path'].tolist()

    return dates


def parse_data_paths(glob_obj, date_format=None, from_date=None, to_date=None, return_dates=False):
    """

    """
    if isinstance(glob_obj, list):
        paths = []
        [paths.extend(glob(p)) for p in glob_obj]
        paths.sort()
    elif isinstance(glob_obj, str):
        paths = glob(glob_obj)

    paths.sort()

    if (from_date is not None) or (to_date is not None) or isinstance(date_format, str):
        paths = filter_data_paths(paths, date_format, from_date, to_date, return_dates)

    return paths


def make_run_date_key(run_date=None):
    """

    """
    if run_date is None:
        run_date = pd.Timestamp.today(tz='utc')
        run_date_key = run_date.strftime('%Y%m%dT%H%M%SZ')
    elif isinstance(run_date, pd.Timestamp):
        run_date_key = run_date.strftime('%Y%m%dT%H%M%SZ')
    elif isinstance(run_date, str):
        run_date1 = pd.Timestamp(run_date).tz_localize(None)
        run_date_key = run_date1.strftime('%Y%m%dT%H%M%SZ')
    else:
        raise TypeError('run_date must be None, Timestamp, or a string representation of a timestamp')

    return run_date_key


def write_json_zstd(data, file_path=None, compress_level=1, retries=3):
    """
    Serializer of a python dictionary to json using orjson then compressed using zstandard.

    Parameters
    ----------
    data : dict
        A dictionary that can be serialized to json using orjson.
    compress_level : int
        zstandard compression level.

    Returns
    -------
    bytes object
    """
    json1 = orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_OMIT_MICROSECONDS | orjson.OPT_SERIALIZE_NUMPY)

    # counter = retries
    # while True:
    #     try:
    #         cctx = zstd.ZstdCompressor(level=compress_level, write_checksum=True, write_content_size=True)
    #         c_obj = cctx.compress(json1)

    #         ## Test
    #         ddtx = zstd.ZstdDecompressor()
    #         _ = ddtx.decompress(c_obj)
    #         break

    #     except Exception as err:
    #         print(str(err))
    #         sleep(2)
    #         counter = counter - 1
    #         if counter <= 0:
    #             raise err

    if isinstance(file_path, (str, pathlib.Path)):
        # source_checksum = zlib.adler32(c_obj)

        # counter = retries
        # while True:
        #     try:
        #         with open(file_path, 'wb') as p:
        #             p.write(c_obj)

        #         ## Test the write
        #         with open(file_path, 'rb') as f:
        #             file_checksum = zlib.adler32(f.read())

        #         if source_checksum == file_checksum:
        #             break
        #         else:
        #             raise ValueError('checksum mismatch...')
        #     except Exception as err:
        #         print(str(err))
        #         sleep(2)
        #         counter = counter - 1
        #         if counter <= 0:
        #             raise err

        with open(file_path, 'wb') as f:
            cctx = zstd.ZstdCompressor(level=compress_level, write_content_size=True)
            with cctx.stream_writer(f, size=len(json1)) as compressor:
                compressor.write(json1)
    else:
        cctx = zstd.ZstdCompressor(level=compress_level, write_content_size=True)
        c_obj = cctx.compress(json1)

        return c_obj


def write_pkl_zstd(obj, file_path=None, compress_level=1, pkl_protocol=pickle.HIGHEST_PROTOCOL, retries=3):
    """
    Serializer using pickle and zstandard. Converts any object that can be pickled to a binary object then compresses it using zstandard. Optionally saves the object to disk. If obj is bytes, then it will only be compressed without pickling.

    Parameters
    ----------
    obj : any
        Any pickleable object.
    file_path : None or str
        Either None to return the bytes object or a str path to save it to disk.
    compress_level : int
        zstandard compression level.

    Returns
    -------
    If file_path is None, then it returns the byte object, else None.
    """
    if isinstance(obj, bytes):
        p_obj = obj
    else:
        p_obj = pickle.dumps(obj, protocol=pkl_protocol)

    # counter = retries
    # while True:
    #     try:
    #         cctx = zstd.ZstdCompressor(level=compress_level, write_checksum=True, write_content_size=True)
    #         c_obj = cctx.compress(p_obj)

    #         ## Test
    #         ddtx = zstd.ZstdDecompressor()
    #         _ = ddtx.decompress(c_obj)
    #         break

    #     except Exception as err:
    #         print(str(err))
    #         sleep(2)
    #         counter = counter - 1
    #         if counter <= 0:
    #             raise err

    if isinstance(file_path, (str, pathlib.Path)):
        # source_checksum = zlib.adler32(c_obj)

        # counter = retries
        # while True:
        #     try:
        #         with open(file_path, 'wb') as p:
        #             p.write(c_obj)

        #         ## Test the write
        #         with open(file_path, 'rb') as f:
        #             file_checksum = zlib.adler32(f.read())

        #         if source_checksum == file_checksum:
        #             break
        #         else:
        #             raise ValueError('checksum mismatch...')
        #     except Exception as err:
        #         print(str(err))
        #         sleep(2)
        #         counter = counter - 1
        #         if counter <= 0:
        #             raise err

        with open(file_path, 'wb') as f:
            cctx = zstd.ZstdCompressor(level=compress_level, write_content_size=True)
            with cctx.stream_writer(f, size=len(p_obj)) as compressor:
                compressor.write(p_obj)
    else:
        cctx = zstd.ZstdCompressor(level=compress_level, write_content_size=True)
        c_obj = cctx.compress(p_obj)

        return c_obj


def grp_ts_agg(df, grp_col, ts_col, freq_code, agg_fun, discrete=False, **kwargs):
    """
    Simple function to aggregate time series with dataframes with a single column of stations and a column of times.

    Parameters
    ----------
    df : DataFrame
        Dataframe with a datetime column.
    grp_col : str, list of str, or None
        Column name that contains the stations.
    ts_col : str
        The column name of the datetime column.
    freq_code : str
        The pandas frequency code for the aggregation (e.g. 'M', 'A-JUN').
    discrete : bool
        Is the data discrete? Will use proper resampling using linear interpolation.

    Returns
    -------
    Pandas DataFrame
    """

    df1 = df.copy()
    if isinstance(df, pd.DataFrame):
        if df[ts_col].dtype.name == 'datetime64[ns]':
            df1.set_index(ts_col, inplace=True)
            if (grp_col is None) or (not grp_col):

                if discrete:
                    df3 = discrete_resample(df1, freq_code, agg_fun, True, **kwargs)
                    df3.index.name = 'time'
                else:
                    df3 = df1.resample(freq_code, **kwargs).agg(agg_fun)

                return df3

            elif isinstance(grp_col, str):
                grp_col = [grp_col]
            elif isinstance(grp_col, list):
                grp_col = grp_col[:]
            else:
                raise TypeError('grp_col must be a str, list, or None')

            if discrete:
                val_cols = [c for c in df1.columns if c not in grp_col]

                grp1 = df1.groupby(grp_col)

                grp_list = []

                for i, r in grp1:
                    s6 = discrete_resample(r[val_cols], freq_code, agg_fun, True, **kwargs)
                    s6[grp_col] = i

                    grp_list.append(s6)

                df2 = pd.concat(grp_list)
                df2.index.name = ts_col

                df3 = df2.reset_index().set_index(grp_col + [ts_col]).sort_index()

            else:
                grp_col.extend([pd.Grouper(level=ts_col, freq=freq_code, **kwargs)])
                df3 = df1.groupby(grp_col).agg(agg_fun)

            return df3

        else:
            raise ValueError('Make one column a timeseries!')
    else:
        raise TypeError('The object must be a DataFrame')


def discrete_resample(df, freq_code, agg_fun, remove_inter=False, **kwargs):
    """
    Function to properly set up a resampling class for discrete data. This assumes a linear interpolation between data points.

    Parameters
    ----------
    df: DataFrame or Series
        DataFrame or Series with a time index.
    freq_code: str
        Pandas frequency code. e.g. 'D'.
    agg_fun : str
        The aggregation function to be applied on the resampling object.
    **kwargs
        Any keyword args passed to Pandas resample.

    Returns
    -------
    Pandas DataFrame or Series
    """
    if isinstance(df, (pd.Series, pd.DataFrame)):
        if isinstance(df.index, pd.DatetimeIndex):
            reg1 = pd.date_range(df.index[0].ceil(freq_code), df.index[-1].floor(freq_code), freq=freq_code)
            reg2 = reg1[~reg1.isin(df.index)]
            if isinstance(df, pd.Series):
                s1 = pd.Series(np.nan, index=reg2)
            else:
                s1 = pd.DataFrame(np.nan, index=reg2, columns=df.columns)
            s2 = pd.concat([df, s1]).sort_index()
            s3 = s2.interpolate('time')
            s4 = (s3 + s3.shift(-1))/2
            s5 = s4.resample(freq_code, **kwargs).agg(agg_fun).dropna()

            if remove_inter:
                index1 = df.index.floor(freq_code).unique()
                s6 = s5[s5.index.isin(index1)].copy()
            else:
                s6 = s5
        else:
            raise ValueError('The index must be a datetimeindex')
    else:
        raise TypeError('The object must be either a DataFrame or a Series')

    return s6


def email_msg(sender_address, sender_password, receiver_address, subject, body, smtp_server="smtp.gmail.com"):
    """
    Function to send a simple email using gmail smtp.

    Parameters
    ----------
    sender_address : str
        The email address of the account that is sending the email.
    sender_password : str
        The password of the sender account.
    receiver_address : str or list of str
        The email addresses of the recipients.
    subject: str
        The subject of the email.
    body : str
        The main body of the email.
    smtp_server : str
        The SMTP server to send the email through.

    Returns
    -------
    None

    """
    port = 465  # For SSL

    msg = EmailMessage()

    # msg_base = """From: {from1}\n
    # To: {to}\n
    # Subject: {subject}\n

    # {body}

    # hostname: {host}
    # IP address: {ip}"""

    ip = requests.get('https://api.ipify.org').text

    body_base = """{body}

    hostname: {host}
    IP address: {ip}"""

    # msg = msg_base.format(subject=subject, body=body, host=socket.getfqdn(), ip=ip, from1=sender_address, to=receiver_address)

    msg['From'] = sender_address
    msg['To'] = receiver_address
    msg['Subject'] = subject
    msg.set_content(body_base.format(body=body, host=socket.getfqdn(), ip=ip))

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_address, sender_password)
        server.send_message(msg)


def tsreg(ts, freq=None, interp=False):
    """
    Function to regularize a time series object (pandas).
    The first three indeces must be regular for freq=None!!!

    Parameters
    ----------
    ts : DataFrame
        pandas time series dataframe.
    freq : str or None
        Either specify the known frequency of the data or use None and
    determine the frequency from the first three indices.
    interp : bool
        Should linear interpolation be applied on all missing data?

    Returns
    -------
    DataFrame
    """

    if freq is None:
        freq = pd.infer_freq(ts.index[:3])
    ts1 = ts.resample(freq).mean()
    if interp:
        ts1 = ts1.interpolate('time')

    return ts1


def create_shifted_df(series, from_range, to_range, freq_code, agg_fun, ref_name, include_0=False, discrete=False, **kwargs):
    """

    """
    if not isinstance(series, pd.Series):
        raise TypeError('series must be a pandas Series.')
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError('The series index must be a pandas DatetimeIndex.')

    df = series.reset_index()
    data_col = df.columns[1]
    ts_col = df.columns[0]
    s2 = grp_ts_agg(df, None, ts_col, freq_code, agg_fun, discrete, **kwargs)[data_col]

    if include_0:
        f_hours = list(range(from_range-1, to_range+1))
        f_hours[0] = 0
    else:
        f_hours = list(range(from_range, to_range+1))

    df_list = []
    for d in f_hours:
        n1 = s2.shift(d, 'H')
        n1.name = ref_name + '_' + str(d)
        df_list.append(n1)
    data = pd.concat(df_list, axis=1).dropna()

    return data


def diagnostic_check(dgn, name):
    """

    """
    if not name in dgn:
        raise ValueError('{} not in diagnostic.'.format(name))

    if not dgn[name]['pass']:
        raise ValueError('{} did not pass the checks. This needs to be run again.'.format(name))


def blake2sum(file_path, buffer_size=256*1024, digest_size=12):
    """
    Function to hash a file using blake2 and iterating over the file via a buffer size to ensure that the function does not use too much memory.

    Parameters
    ----------
    file_path : str or Path object
        The path to the file to be hashed.
    buffer_size : int
        The buffer size in bytes.
    digest_size : int
        The digest size for the blake2 algorithum.

    Returns
    -------
    str
        hex hash of the file.
    """
    h = hashlib.blake2b(digest_size=digest_size)
    # h = blake3()
    buffer = bytearray(buffer_size)
    # using a memoryview so that we can slice the buffer without copying it
    buffer_view = memoryview(buffer)
    with open(file_path, 'rb', buffering=0) as f:
        while True:
            n = f.readinto(buffer_view)
            if not n:
                break
            h.update(buffer_view[:n])
    return h.hexdigest()
    # return h.hexdigest(digest_size)


def clear_xr_objects():
    """

    """
    n_cleaned = 0
    objs = list(globals())
    for obj in objs:
        if isinstance(globals()[obj], (xr.DataArray, xr.Dataset)):
            globals()[obj].close()
            del globals()[obj]
            n_cleaned = n_cleaned + 1

    return n_cleaned


def check_compressor(obj):
    """

    """
    cctx = zstd.ZstdCompressor(level=1, write_checksum=True, write_content_size=True)
    c_obj = cctx.compress(obj)

    ## Test
    ddtx = zstd.ZstdDecompressor()
    _ = ddtx.decompress(c_obj)


def check_writing(obj, base_path):
    """

    """
    id1 = uuid.uuid4().hex
    file_path = os.path.join(base_path, id1 + '.zst')
    source_checksum = zlib.adler32(obj)

    with open(file_path, 'wb') as p:
        p.write(obj)

    ## Test the write
    with open(file_path, 'rb') as f:
        file_checksum = zlib.adler32(f.read())

    if source_checksum != file_checksum:
        raise ValueError('checksum mismatch...')
























