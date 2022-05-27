#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:43:15 2021

@author: mike
"""
import pandas as pd
from io import BytesIO
import xarray as xr
import os
import gzip
import shutil
import requests
import orjson
import copy
import multiprocessing as mp
import pathlib
from tethysts.utils import get_object_s3, url_stream_to_file, read_pkl_zstd, b2_public_key_pattern
import gzip
import zstandard as zstd
import subprocess
import glob
import rioxarray as rxr
import concurrent.futures
# mp.set_start_method('spawn')

##########################################
### Functions


def query_esri_mapserver(base_url, layer_id, out_fields=None, where=None):
    """
    Query an ESRI map server for a vector layer and return a geojson structured dict.

    Parameters
    ----------
    base_url : str
        The base url for the map server up to the layer_id.
    layer_id : str or int
        The layer id.
    out_fields : None or list of str
        The output fields to be returned. The geometry will always be returned. None will return all fields.
    where : None or str
        The SQL style 'where' clause to query the layer. None will have no filters.

    Returns
    -------
    Dict
        In GeoJSON structure
    """
    url = base_url + str(layer_id) + '/query'

    ## Set up filters
    params = {'returnGeometry': 'true', 'f': 'geojson'}

    if out_fields is None:
        params.update({'outFields': '*'})
    elif isinstance(out_fields, list):
        out_str = ', '.join(out_fields)
        params.update({'outFields': out_str})
    else:
        raise ValueError('out_fields must either be None or a list of strings')

    if where is None:
        params.update({'where': '1=1'})
    elif isinstance(where, str):
        params.update({'where': where})
    else:
        raise ValueError('where must either be None or a string')

    ## Run the queries
    resp = requests.get(url, params=params, timeout=300)

    if not resp.ok:
        raise ValueError(resp.raise_for_status())

    data = orjson.loads(resp.content)

    if 'exceededTransferLimit' in data:
        exceed = data.pop('exceededTransferLimit')
    else:
        exceed = False

    data_all = copy.deepcopy(data)

    while exceed:
        last_id = data['features'][-1]['id']

        if isinstance(where, str):
            params.update({'where': where + 'and objectid > ' + str(last_id)})
        else:
            params.update({'where': 'objectid > ' + str(last_id)})

        resp = requests.get(url, params=params, timeout=300)

        if not resp.ok:
            raise ValueError(resp.raise_for_status())

        data = orjson.loads(resp.content)

        data_all['features'].extend(data['features'])

        if 'exceededTransferLimit' in data:
            exceed = data.pop('exceededTransferLimit')
        else:
            exceed = False

    return data_all



def decompress_file(source_path, dest_path=None, compression_type='gzip', buffer_size=5242880):
    if not isinstance(dest_path, str):
        dest_path = os.path.splitext(source_path)[0]
    with gzip.open(source_path, 'rb') as s_file, open(dest_path, 'wb') as d_file:
        shutil.copyfileobj(s_file, d_file, buffer_size)

    return dest_path


def dfd(source_path):
    dest_path = decompress_file(source_path)
    os.remove(source_path)
    return dest_path


def decompress_files_remove(source_paths, max_workers=4):
    """

    """

    # with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
    #     results = executor.map(dfd, source_paths)
    with mp.get_context("spawn").Pool(processes=max_workers) as pool:
        results = pool.map(dfd, source_paths)

    return results


def convert_grib_to_nc(source_path):
    """

    """
    dest_path = os.path.splitext(source_path)[0]
    dest_path = dest_path + '.nc'
    cmd_str = 'cdo -s -O -f nc4 copy {in_file} {out_file}'.format(in_file=source_path, out_file=dest_path)

    _ = subprocess.run(cmd_str, shell=True, check=True)

    # cdo = Cdo()
    # cdo.copy(input=source_path, output=dest_path, options = "-O -f nc4")

    return dest_path


def convert_grib_remove(source_path):
    dest_path = convert_grib_to_nc(source_path)
    os.remove(source_path)
    return dest_path


def convert_gribs_remove(source_paths, max_workers=4):
    """

    """
    with mp.get_context("spawn").Pool(processes=max_workers) as pool:
        results = pool.map(convert_grib_remove, source_paths)

    return results


def convert_geotiff_to_nc(source_path, time, height, x_name='x', y_name='y', band=1):
    """

    """
    time1 = pd.Timestamp(time)

    xr1 = rxr.open_rasterio(source_path)
    xr1 = xr1.rename({x_name: 'lon', y_name: 'lat'}).sel(band=band).drop('band')
    xr1 = xr1.assign_coords(height=height).expand_dims('height', axis=2)
    xr1 = xr1.assign_coords(time=time1).expand_dims('time')
    xr1.name = 'raster'

    attrs = xr1.attrs.copy()

    encoding = {'dtype': xr1.encoding['rasterio_dtype'], 'scale_factor': attrs['scale_factor'], 'add_offset': attrs['add_offset'], '_FillValue': -9999}

    xr1.encoding = encoding
    xr1.attrs = {}

    dest_path = os.path.splitext(source_path)[0]
    dest_path = dest_path + '.nc'

    xr1.to_netcdf(dest_path)

    os.remove(source_path)

    return dest_path


def convert_geotiffs_to_nc(source_paths, time, height, x_name='x', y_name='y', band=1, max_workers=4):
    """

    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for source_path in source_paths:
            f = executor.submit(convert_geotiff_to_nc, source_path, time, height, x_name, y_name, band)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    new_paths = [r.result() for r in runs[0]]

    return new_paths


def copy_file(source_path, dest_path, compression=None, chunk_size=524288):
    dest_path1 = pathlib.Path(dest_path)
    if dest_path1.is_dir():
        source_path1 = pathlib.Path(source_path)
        file_name = source_path1.name
        dest_path2 = str(dest_path1.joinpath(file_name))
    else:
        dest_path2 = dest_path

    if compression == 'gzip':
        if dest_path2.endswith('.gz'):
            dest_path2 = os.path.splitext(dest_path2)[0]
        with gzip.open(source_path, 'rb') as s_file, open(dest_path2, 'wb') as d_file:
            shutil.copyfileobj(s_file, d_file, chunk_size)
    elif compression == 'zstd':
        if dest_path2.endswith('.zst'):
            dest_path2 = os.path.splitext(dest_path2)[0]
        with open(source_path, 'rb') as s_file, open(dest_path2, 'wb') as d_file:
            dctx = zstd.ZstdDecompressor()
            dctx.copy_stream(s_file, d_file, read_size=chunk_size, write_size=chunk_size)
    else:
        shutil.copyfile(source_path, dest_path2)

    return dest_path2


def mergetime_nc_files(nc_paths, by):
    """

    """
    path1 = pathlib.Path(nc_paths[0])
    parent_path = path1.parent

    if by == 'dataset':
        ds_id = path1.stem.split('_')[0]
        file_name = ds_id + '.nc'
    elif by == 'station':
        ds_id, stn_id, date = path1.stem.split('_')
        file_name = '{}_{}.nc'.format(ds_id, stn_id)

    dest_path = str(parent_path.joinpath(file_name))
    source_paths = ' '.join(nc_paths)

    cmd_str = 'cdo -s -O mergetime {in_files} {out_file}'.format(in_files=source_paths, out_file=dest_path)

    _ = subprocess.run(cmd_str, shell=True, check=True)

    # cdo = Cdo()
    # _ = cdo.mergetime(input=source_paths, output=dest_path)

    return dest_path


def mergetime_nc_remove(source_paths, by):
    dest_path = mergetime_nc_files(source_paths, by)
    for p in source_paths:
        os.remove(p)
    return dest_path


def gdal_merge(source_paths, dest_path, compression='ZSTD'):
    """
    Uses gdal_merge.py to merge many rasters together using a defined compression to a GeoTiff. The compression must be one of the COMPRESS options for GeoTiffs:
        https://gdal.org/drivers/raster/gtiff.html#raster-gtiff
    """
    f2 = source_paths.copy()
    f2.sort()

    source_paths_str = ' '.join(f2)

    if not dest_path.endswith('.tif'):
        raise ValueError('The dest_path must be a file path with a .tif extension.')

    cmd_str = 'gdal_merge.py -co COMPRESS={compression} -o {out_file} {in_files}'.format(in_files=source_paths_str, out_file=dest_path, compression=compression)

    _ = subprocess.run(cmd_str, shell=True, check=True)


def copy_s3_file(source_path, dest_path, bucket, s3=None, connection_config=None, public_url=None, compression=None, chunk_size=524288):
    """

    """
    file_path1 = pathlib.Path(dest_path)
    if file_path1.is_dir():
        file_name = source_path.split('/')[-1]
        file_path2 = str(file_path1.joinpath(file_name))
    else:
        file_path2 = dest_path

    base_path = os.path.split(file_path2)[0]
    os.makedirs(base_path, exist_ok=True)

    counter = 5
    while True:
        if counter < 1:
            raise gzip.BadGzipFile('Too many crc32 errors for: ' + source_path)
        try:
            if isinstance(public_url, str):
                url1 = b2_public_key_pattern.format(base_url=public_url.rstrip('/'), bucket=bucket, obj_key=source_path)
                file_path3 = url_stream_to_file(url1, file_path2, compression=compression, chunk_size=chunk_size)
            else:
                url1 = get_object_s3(source_path, connection_config=connection_config, bucket=bucket, counter=5)
                if compression == 'zstd':
                    if file_path2.endswith('.zst'):
                        file_path2 = os.path.splitext(file_path2)[0]
                    url1 = read_pkl_zstd(url1)
                elif compression == 'gzip':
                    if file_path2.endswith('.gz'):
                        file_path2 = os.path.splitext(file_path2)[0]
                    url1 = gzip.decompress(url1)
                b1 = BytesIO(url1)
                with open(file_path2, 'wb') as f:
                    chunk = b1.read(chunk_size)
                    while chunk:
                        f.write(chunk)
                        chunk = b1.read(chunk_size)

                file_path3 = file_path2
            break
        except gzip.BadGzipFile:
            print('crc32 gzip error for: ' + source_path)
            counter = counter - 1

    return file_path3
