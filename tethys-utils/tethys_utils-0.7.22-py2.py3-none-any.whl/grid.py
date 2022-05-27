#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  4 14:24:46 2022

@author: mike
"""
import os
import numpy as np
import xarray as xr
import pandas as pd
from tethys_utils import misc, s3, processing, titan, data_io
from tethysts.utils import s3_client, get_object_s3, read_json_zstd, read_pkl_zstd, download_results, create_public_s3_url
import tethys_data_models as tdm
from typing import List, Optional, Dict, Union
import pandas as pd
from pydantic import HttpUrl
import concurrent.futures
import copy
import pathlib
import dask
import glob
from datetime import date, datetime
import multiprocessing as mp
import pyproj
from time import sleep


###############################################
### Parameters

interim_file_str = '{ds_id}_{stn_id}_{date}.nc'

dask.config.set(**{'array.slicing.split_large_chunks': False})


###############################################
### Helper functions


def multi_save_dataset_stations(nc_paths, block_length, block_length_factor: int = 10, compression='zstd', remove_station_data=True, max_workers=3):
    """

    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    ## Iterate through files
    if max_workers <= 1:

        nc_paths = []
        for nc_path in nc_paths1:
            new_paths0 = processing.save_dataset_stations(nc_path, block_length * block_length_factor, compression=compression, remove_station_data=remove_station_data)
            nc_paths.append(new_paths0)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
            futures = []
            for nc_path in nc_paths1:
                f = executor.submit(processing.save_dataset_stations, nc_path, block_length * block_length_factor, compression=compression, remove_station_data=remove_station_data)
                futures.append(f)
            runs = concurrent.futures.wait(futures)

        new_paths = [r.result() for r in runs[0]]

    ## process output
    new_paths1 = []
    for new_path in new_paths:
        new_paths1.extend(new_path)

    new_paths1.sort()

    return new_paths1


def estimate_time_interval_accurate(data, block_length, null_grid=None, max_mb=2):
    """

    """
    ## Get the dimension data
    dims = dict(data.dims)

    ## Test requested block_length
    chunks_list = processing.chunk_data(data, block_length=block_length, time_interval=None, null_grid=null_grid)

    dim_sizes = np.array([np.prod(list(c.dims.values())) for c in chunks_list])
    max_dim_index = np.argsort(dim_sizes)[-10:]
    sum_dim_objs = np.sum(dim_sizes[max_dim_index])

    sum_chunks = 0
    for i in max_dim_index:
        chunk = chunks_list[i].copy().load()
        obj_len = len(misc.write_pkl_zstd(chunk.to_netcdf()))

        sum_chunks += obj_len

        chunk.close()
        del chunk

    dim_per_mb = int(sum_dim_objs/(sum_chunks * 0.000001))

    if 'geometry' in dims:
        geo_sizes = np.array([c.dims['geometry'] for c in chunks_list])
    else:
        geo_sizes = np.array([c.dims['lon'] * c.dims['lat'] for c in chunks_list])

    max_geo_size = np.max(geo_sizes)

    times_per_mb = (dim_per_mb/max_geo_size)

    ## Calc time_interval
    times1 = pd.to_datetime(data['time'].values)
    days = times1.floor('D').drop_duplicates()
    times_per_day = len(times1)/len(days)

    days_per_mb = times_per_mb/times_per_day

    days_per_chunk = int(days_per_mb * max_mb)

    ## Test final parameters
    chunks_list = processing.chunk_data(data, block_length=block_length, time_interval=days_per_chunk, null_grid=null_grid)

    n_chunks = len(chunks_list)

    _ = [c.close() for c in chunks_list]
    del chunks_list

    output_dict = {'time_interval': days_per_chunk,
                   'n_geometries_per_station': max_geo_size,
                   'n_chunks': n_chunks,
                   'values_per_mb': dim_per_mb
                   }

    return output_dict


def bulk_estimate_time_interval(data, block_lengths, null_grid=None, max_mb=2):
    """

    """
    block_length_dict = {}
    for b in block_lengths:
        print(b)
        o1 = estimate_time_interval_accurate(data, b, null_grid, max_mb)
        block_length_dict[b] = o1

    return block_length_dict


def estimate_time_interval_rough(data_grid_length, time_freq, block_lengths, max_mb=2, values_per_mb=550000):
    """
    Function to roughly estimate the appropriate time intervals based on specific block lengths.

    Parameters
    ----------
    data_grid_length: float or int
        The grid resolution.
    time_freq: str
        The time resolution in pandas time freq format.
    block_lengths: list of float
        The block lengths to test. Should be equal to or greater than the data_grid_length.
    max_mb: float or int
        The max size of the results object.
    values_per_mb: int
        The number of data values in a results object per MB. Do not change unless you've done the testing to determine this value.
    """
    t1 = pd.date_range('2000-01-01', '2000-01-08', freq = time_freq)[:-1]
    val_per_day = len(t1)/7

    total_val_per_day = max_mb * values_per_mb

    res_list = []
    for bl in block_lengths:
        n_stns = int(np.ceil((bl**2)/(data_grid_length**2)))
        days_per_chunk = int(total_val_per_day/n_stns/val_per_day)
        dict1 = {'time_interval': days_per_chunk,
                 'n_geometries_per_station': n_stns}
        res_list.append(dict1)

    res_dict = {bl: res_list[i] for i, bl in enumerate(block_lengths)}

    return res_dict


def decompress_path(glob_path, compression_type='gzip', max_workers=4, **kwargs):
    """

    """
    if isinstance(glob_path, str):
        files1 = glob.glob(glob_path)
    elif isinstance(glob_path, list):
        files1 = glob_path
    new_files = data_io.decompress_files_remove(files1, max_workers=max_workers)

    return new_files


def file_format_conversion(glob_path, file_format='grib', max_workers=4, **kwargs):
    """
    Function to convert data files to netcdf files.
    """
    if isinstance(glob_path, str):
        files1 = glob.glob(glob_path)
    elif isinstance(glob_path, list):
        files1 = glob_path

    if file_format == 'grib':
        new_files = data_io.convert_gribs_remove(files1, max_workers=max_workers)
    else:
        raise NotImplementedError('file_format not available.')
    # elif file_format == 'geotiff':
    #     new_files = data_io.convert_geotiffs_to_nc(files1, max_workers=max_workers, **kwargs)

    return new_files


def get_obj_list(glob_path, date_format=None, freq=None, from_date=None, to_date=None, connection_config=None, bucket=None):
    """

    """
    glob_path2 = glob_path

    if isinstance(connection_config, dict) and isinstance(bucket, str):
        if glob_path2.startswith('/'):
            glob_path2 = glob_path2[1:]
        glob_path3, glob_ext = os.path.split(glob_path2)
        if not glob_path3.endswith('/'):
            glob_path3 = glob_path3 + '/'
        client = s3_client(connection_config)
        obj_list = s3.list_objects_s3(client, bucket, glob_path3, delimiter='/', date_format=date_format)
        obj_list1 = obj_list.rename(columns={'Key': 'path', 'Size': 'size', 'KeyDate': 'date'}).drop(['LastModified', 'ETag'], axis=1).copy()
        # obj_list1['remote_type'] = 's3'
    else:
        files1 = glob.glob(glob_path)
        sizes = [os.path.getsize(f) for f in files1]
        obj_list1 = pd.DataFrame(zip(files1, sizes), columns=['path', 'size'])
        # obj_list1['remote_type'] = 'local'

        if isinstance(date_format, str):
            dates1 = misc.filter_data_paths(obj_list1.path, date_format, return_dates=True)
            obj_list1 = pd.merge(obj_list1, dates1, on='path')

    filter1 = [pathlib.Path(p).match(glob_path2) for p in obj_list1.path.values]
    obj_list2 = obj_list1.iloc[filter1]

    if isinstance(date_format, str):
        if isinstance(from_date, (str, pd.Timestamp, date, datetime)):
            obj_list2 = obj_list2[obj_list2['date'] >= pd.Timestamp(from_date)].copy()
        if isinstance(to_date, (str, pd.Timestamp, date, datetime)):
            obj_list2 = obj_list2[obj_list2['date'] < pd.Timestamp(to_date)].copy()

    if isinstance(freq, str):
        grp1 = obj_list2.groupby(pd.Grouper(key='date', freq=freq, origin='start'))

        obj_list3 = [v for k, v in grp1]
    else:
        obj_list3 = obj_list2

    return obj_list3


def copy_source_objs(source_paths, dest_path, bucket=None, connection_config=None, public_url=None, compression=None, threads=None, max_workers=None):
    """

    """
    objs = source_paths

    if isinstance(connection_config, (dict, str)) and isinstance(bucket, str):
        client = s3_client(connection_config, threads)

        if isinstance(max_workers, int):

            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
                futures = []
                for obj in objs:
                    f = executor.submit(data_io.copy_s3_file, source_path=obj, dest_path=dest_path, connection_config=connection_config, bucket=bucket, public_url=public_url, compression=compression)
                    futures.append(f)
                runs = concurrent.futures.wait(futures)

            new_paths = [r.result() for r in runs[0]]

        else:
            if threads is None:
                threads = 4

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for obj in objs:
                    f = executor.submit(data_io.copy_s3_file, source_path=obj, dest_path=dest_path, s3=client, connection_config=connection_config, bucket=bucket, public_url=public_url, compression=compression)
                    futures.append(f)
                runs = concurrent.futures.wait(futures)

            new_paths = [r.result() for r in runs[0]]

    else:
        new_paths = []
        for obj in objs:
            path1 = data_io.copy_file(source_path=obj, dest_path=dest_path, compression=compression)
            new_paths.append(path1)

    new_paths.sort()

    return new_paths


def copy_interim_objs(source_paths, dest_path, bucket, connection_config=None, public_url=None, threads=20):
    """

    """
    client = s3_client(connection_config, threads)

    path1 = pathlib.Path(dest_path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for source_path in source_paths:
            p_list = source_path.split('/')
            ds_id = p_list[4]
            stn_id, date, nc, z = p_list[5].split('.')

            file_name = interim_file_str.format(ds_id=ds_id, stn_id=stn_id, date=date)
            dest_path1 = str(path1.joinpath(file_name))

            f = executor.submit(data_io.copy_s3_file, source_path, dest_path1, bucket, s3=client, public_url=public_url, compression='zstd')
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    new_paths = [r.result() for r in runs[0]]

    new_paths.sort()

    return new_paths


def variable_processing(nc_paths, time_name, x_name, y_name, variables, projected_coordinates=True, nc_source='normal', max_workers=4):
    """
    The variable processing function does three things:
        - select only the specific variables that should be exported,
        - restructure (transpose in xarray) the coordinates so that they are ordered by time, y, x, height,
        - remove duplicate overlapping timestamps between files.

    The restructuring of the coordinates must make sure that the time coordinate is called "time", but the x and y coordinates do not necessarily need to be modified. They just need to be in the correct order. If they are actually longitude and latitude, changing them to lon and lat will make things easier in the future.
    This process will iterate over all of the nc files rather than trying to open them and process them using Dask and xarray. They will initially be opened in Dask to determine the overlapping times only.

    Parameters
    ----------
    nc_paths : list of str or glob str
        The paths to the nc files to be processed.
    variables : list of str
        The variables that should be extracted from the nc files.
    time_index_bool : list of bool
        The boolean time index in case only one file is pulled down to be processed. Normally this should not be needed as there will be multiple files to determine the overlapping times.
    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    nc_paths1.sort()

    ## Determine duplicate times
    if len(nc_paths1) > 1:
        time_index_bool = processing.determine_duplicate_times(nc_paths1, time_name)
    else:
        time_index_bool = None

    ## Iterate through files
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for nc_path in nc_paths1:
            f = executor.submit(processing.preprocess_data_structure, nc_path, time_name, x_name, y_name, variables, time_index_bool, projected_coordinates)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    ## process output
    new_paths = [r.result() for r in runs[0]]
    new_paths1 = []
    for new_path in new_paths:
        new_paths1.extend(new_path)

    new_paths1.sort()

    return new_paths1


def resample_to_wgs84_grids(nc_paths, proj4_crs, order=1, min_val=None, max_val=None, bbox=None, time_name='time', x_name='x', y_name='y', max_workers=4):
    """

    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    xr1 = xr.open_dataset(nc_paths1[0])

    ## Get approximate grid resolution
    x1 = xr1[x_name].values
    half_x = len(x1)//2
    x = x1[half_x:(half_x+10)]

    y1 = xr1[y_name].values
    half_y = len(y1)//2
    y = y1[half_y:(half_y+10)]

    xr1.close()
    del xr1

    wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')

    trans = pyproj.Transformer.from_proj(proj4_crs, wgs84)

    lon, lat = trans.transform(x, y)

    grid_res_lat = np.quantile(np.abs(np.diff(lat.T)), 0.5)
    grid_res_lon = np.quantile(np.abs(np.diff(lon.T)), 0.5)
    grid_res = round((grid_res_lon + grid_res_lat)/2, 5)

    ## Iterate through files
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for nc_path in nc_paths1:
            f = executor.submit(processing.resample_to_wgs84_grid, nc_path, proj4_crs, grid_res, order, min_val, max_val, bbox)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    ## process output
    print('grid resolution/length is: ' + str(grid_res))
    new_paths = [r.result() for r in runs[0]]
    new_paths.sort()

    return new_paths


# def calc_new_parameters():
#     """

#     """
#     dates1 = misc.filter_data_paths(obj_list1.path, date_format, return_dates=True)



def combine_metadata(project, dataset):
    """

    """
    datasets = []
    for d in dataset:
        d1 = copy.deepcopy(d)
        d1.update(project)
        datasets.append(d1)

    return datasets


def multi_calc_new_variables(nc_paths, dataset_codes_dict, version_date, func_dict):
    """

    """
    dates1 = misc.filter_data_paths(nc_paths, '%Y%m%d%H%M%S', return_dates=True)
    dates1['variable'] = dates1.path.apply(lambda x: pathlib.Path(x).stem.split('_wgs84_')[0])

    ## Iterate through files
    # if max_workers <=1:
    new_paths_list = []
    for i, g in dates1.groupby('date'):
        # print(g)
        p = processing.calc_new_variables(g['path'].tolist(), dataset_codes_dict, version_date, func_dict)
        new_paths_list.append(p)

    # elif max_workers > 1:
    #     with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
    #         futures = []
    #         for i, g in dates1.groupby('date'):
    #             # print(g)
    #             f = executor.submit(processing.calc_new_variables, g['path'].tolist(), datasets, func_dict)
    #             futures.append(f)
    #         runs = concurrent.futures.wait(futures)

    #     # process output
    #     new_paths_list = [r.result() for r in runs[0]]

    new_paths1 = []
    for new_path in new_paths_list:
        new_paths1.extend(new_path)

    new_paths1.sort()

    return new_paths1


def multi_mergetime_nc_remove(source_paths, by, max_workers=3):
    """

    """
    source_paths_dict = {}
    if by == 'dataset':
        for p in source_paths:
            path1 = pathlib.Path(p)
            ds_id = path1.stem.split('_')[0]
            if ds_id in source_paths_dict:
                source_paths_dict[ds_id].append(p)
            else:
                source_paths_dict[ds_id] = [p]
    elif by == 'station':
        for p in source_paths:
            path1 = pathlib.Path(p)
            ds_id, stn_id, date = path1.stem.split('_')
            key = (ds_id, stn_id)
            if key in source_paths_dict:
                source_paths_dict[key].append(p)
            else:
                source_paths_dict[key] = [p]
    else:
        raise ValueError('by must be either dataset or station.')

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for ds_id, paths in source_paths_dict.items():
            f = executor.submit(data_io.mergetime_nc_remove, paths, by)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    new_paths = [r.result() for r in runs[0]]
    new_paths.sort()

    return new_paths











###############################################
### Main class


class Grid(titan.Titan):
    """

    """
    def load_dataset_metadata(self, dataset_codes: List[str], project_metadata, func_dict=None):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'status_checks')

        if hasattr(self, '_func_dict'):
            func_dict1 = self._func_dict
        elif func_dict is not None:
            func_dict1 = func_dict
        else:
            raise ValueError('func_dict must not be None.')

        datasets_dict = {}
        for d in dataset_codes:
            if d in func_dict1:
                d1 = copy.deepcopy(func_dict1[d]['metadata'])
                d1.update(project_metadata)
                datasets_dict[d] = d1
            else:
                raise ValueError('The dataset code {} is not available.'.format(d))

        dataset_list = processing.process_datasets(datasets_dict)

        datasets_dict = {ds_code: ds[0] for ds_code, ds in datasets_dict.items()}

        # TODO: Check for existing datasets in other S3 buckets

        ## Check if the chunking parameters are in the datasets
        for ds in dataset_list:
            if 'chunk_parameters' in ds:
                _ = tdm.dataset.ChunkParams(**ds['chunk_parameters'])
            elif ds['method'] in ['sensor_recording', 'field_activity', 'sample_analysis']:
                print('Default chunk_parameters have been set.')
                ds['chunk_parameters'] = {'block_length': 0, 'time_interval': 7300}
            else:
                raise ValueError('chunk_parameters have not been set in the dataset metadata. Please do so.')

        ## Validate dataset model
        for ds in dataset_list:
            _ = tdm.dataset.Dataset(**ds)

        ## Set attributes
        ds_dict = {ds['dataset_id']: ds for ds in dataset_list}

        setattr(self, 'dataset_list', dataset_list)
        setattr(self, 'datasets', ds_dict)
        setattr(self, 'dataset_codes_dict', datasets_dict)
        setattr(self, 'func_dict', func_dict1)

        ## diagnostic log
        self.diagnostics['load_dataset_metadata'] = {'pass': True}
        self.diagnostics['attributes'].update({'dataset_list': dataset_list, 'datasets': ds_dict, 'dataset_codes_dict': datasets_dict})


    def get_obj_list(self, glob_path, date_format=None, freq=None, from_date=None, to_date=None, source_connection_config=None, source_bucket=None, source_public_url=None):
        """

        """
        obj_list = get_obj_list(glob_path, date_format=date_format, freq=freq, from_date=from_date, to_date=to_date, connection_config=source_connection_config, bucket=source_bucket)

        # self.obj_list = obj_list.path.tolist()
        self.source_connection_config = source_connection_config
        self.source_bucket = source_bucket
        self.source_public_url = source_public_url

        ## diagnostic log
        self.diagnostics['get_obj_list'] = {'pass': True}
        self.diagnostics['attributes'].update({'source_connection_config': source_connection_config, 'source_bucket': source_bucket, 'source_public_url': source_public_url})

        return obj_list


    def copy_source_objs(self, source_paths, compression=None, threads=None, max_workers=None):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'get_obj_list')

        new_paths = copy_source_objs(source_paths, self.preprocessed_path, threads=threads, compression=compression, connection_config=self.source_connection_config, bucket=self.source_bucket, public_url=self.source_public_url, max_workers=max_workers)

        return new_paths


    # def decompress_files(self, source_paths, compression_type='gzip', max_workers=4):
    #     """

    #     """
    #     new_paths1 = decompress_path(source_paths, compression_type=compression_type, max_workers=max_workers)

    #     return new_paths1


    def file_format_conversion(self, source_paths, file_format='grib', max_workers=4, **kwargs):
        """

        """
        new_paths2 = file_format_conversion(source_paths, file_format=file_format, max_workers=max_workers, **kwargs)

        return new_paths2


    def variable_processing(self, source_paths, time_name, x_name, y_name, projected_coordinates=True, nc_source='normal', max_workers=4):
        """

        """
        ## Determine the variables needed to be extracted
        dataset_codes = list(self.dataset_codes_dict.keys())

        variables_set = set()
        for d in dataset_codes:
            v1 = self.func_dict[d]['variables']
            variables_set.update(v1)

        variables = list(variables_set)
        variables.sort()

        ## Run the processing
        new_paths2 = variable_processing(source_paths, time_name, x_name, y_name, variables, projected_coordinates=projected_coordinates, max_workers=max_workers)

        return new_paths2


    def resample_to_wgs84(self, source_paths, proj4_crs, order=2, bbox=None, max_workers=4):
        """

        """
        new_paths2 = resample_to_wgs84_grids(source_paths, proj4_crs, order=order, bbox=bbox, max_workers=max_workers)

        return new_paths2


    def calc_new_variables(self, source_paths):
        """

        """
        new_paths2 = multi_calc_new_variables(source_paths, self.dataset_codes_dict, self.max_version_date, self.func_dict)

        return new_paths2


    def merge_time_nc_files(self, source_paths, by, max_workers=4):
        """

        """
        # if by == 'station':
        #     misc.diagnostic_check(self.diagnostics, 'copy_interim_objs')

        new_paths = multi_mergetime_nc_remove(source_paths, by=by, max_workers=max_workers)

        if by == 'station':
            ## diagnostic log
            self.diagnostics['merge_nc_files'] = {'pass': True}

        return new_paths


    def save_dataset_stations(self, source_paths, block_length, block_length_factor=10, compression='zstd', max_workers=4):
        """

        """
        new_paths = multi_save_dataset_stations(source_paths, block_length, block_length_factor=block_length_factor, compression=compression, max_workers=max_workers)

        return new_paths


    def upload_interim_results(self, source_paths, threads=10):
        """

        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            client = s3_client(self.connection_config, max_pool_connections=threads)
            futures = []
            for path in source_paths:
                f = executor.submit(s3.put_interim_results_s3, client, self.bucket, path, self.run_id, system_version=self.system_version)
                futures.append(f)
            runs = concurrent.futures.wait(futures)

        keys = [r.result() for r in runs[0]]

        self.interim_keys = keys

        ## Remove source files
        for path in source_paths:
            os.remove(path)

        ## diagnostic log
        # self.diagnostics['upload_interim_results'] = {'pass': True}
        # self.diagnostics['attributes'].update({'interim_keys': keys})

        return keys


    def get_interim_results_list(self, max_size_gb=0.1):
        """

        """
        ## Checks
        misc.diagnostic_check(self.diagnostics, 'status_checks')

        ## Prepare
        max_size = max_size_gb * 1000000000

        key_pattern = tdm.key_patterns[self.system_version]['interim_results'].split('{dataset_id}')[0]
        key = key_pattern.format(run_id=self.run_id)

        ## Query objects
        client = s3_client(self.connection_config)
        obj_list1 = s3.list_objects_s3(client, self.bucket, key)
        obj_list1 = obj_list1[['Key', 'Size']].rename(columns={'Key': 'key', 'Size': 'size'})

        obj_keys1 = obj_list1['key'].tolist()
        ds_keys2 = [k.split('/')[4] for k in obj_keys1]
        stn_keys2 = [k.split('/')[5].split('.')[0] for k in obj_keys1]

        obj_list1['dataset_id'] = ds_keys2
        obj_list1['station_id'] = stn_keys2

        # ds_sizes = obj_list1.groupby('dataset_id')['size'].sum().reset_index()
        ds_stn_sizes = obj_list1.groupby(['dataset_id', 'station_id'])['size'].sum().reset_index().sort_values('size', ascending=False)

        ## Test to make sure the max size is bigger than the largest file
        if ds_stn_sizes.iloc[0]['size'] > max_size:
            raise ValueError('The max_size_gb must be larger than the largest object: {} GB.'.format(round(ds_stn_sizes.iloc[0]['size'] / 1000000000, 2)))

        ## Split the objects
        interim_groups = []

        while True:
            ds_stn_sizes['cumsum'] = ds_stn_sizes['size'].cumsum()
            ds_stn_set = ds_stn_sizes[ds_stn_sizes['cumsum'] < max_size]

            if ds_stn_set.empty:
                break
            else:
                ig = pd.merge(ds_stn_set[['dataset_id', 'station_id']], obj_list1, on=['dataset_id', 'station_id'])
                ds_stn_sizes = ds_stn_sizes[ds_stn_sizes['cumsum'] >= max_size].copy()

                interim_groups.append(ig)

        ## diagnostic log
        self.diagnostics['get_interim_results_list'] = {'pass': True}
        # self.diagnostics['attributes'].update({'interim_objects': obj_list1, 'ds_stn_sizes': ds_stn_sizes, 'ds_sizes': ds_sizes})

        return interim_groups


    def copy_interim_objs(self, source_paths, threads=20):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'get_interim_results_list')

        new_paths = copy_interim_objs(source_paths, self.preprocessed_path, threads=threads, connection_config=self.connection_config, bucket=self.bucket, public_url=self.public_url)

        ## diagnostic log
        self.diagnostics['copy_interim_objs'] = {'pass': True}

        return new_paths


    def clear_interim_results(self):
        """

        """
        prefix = tdm.utils.key_patterns[self.system_version]['interim_results'].split('{dataset_id}')[0].format(run_id=self.run_id)

        client = s3_client(self.connection_config)

        obj_list = s3.list_object_versions_s3(client, self.bucket, prefix)

        rem_keys = []
        for i, row in obj_list.iterrows():
            rem_keys.extend([{'Key': row['Key'], 'VersionId': row['VersionId']}])

        if len(rem_keys) > 0:
            ## Split them into 1000 key chunks
            rem_keys_chunks = np.array_split(rem_keys, int(np.ceil(len(rem_keys)/1000)))

            ## Run through and delete the objects...
            for keys in rem_keys_chunks:
                _ = client.delete_objects(Bucket=self.bucket, Delete={'Objects': keys.tolist(), 'Quiet': True})

        print(str(len(rem_keys)) + ' objects removed')






















































