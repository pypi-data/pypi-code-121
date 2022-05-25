#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 13:31:09 2021

@author: mike
"""
import os
import xarray as xr
import numpy as np
import pandas as pd
import copy
import orjson
from hashlib import blake2b
import tethys_data_models as tdm
from tethys_utils.misc import make_run_date_key, write_pkl_zstd, write_json_zstd
import geojson
from shapely.geometry import shape, mapping, box, Point, Polygon, MultiPoint
from shapely import wkb, wkt
from tethysts import utils
from time import sleep
import pathlib
from hydrointerp import Interp
import numcodecs
import glob
import rioxarray as rxr
from typing import List, Optional, Dict, Union
import concurrent.futures
import multiprocessing as mp
import zlib
import zstandard as zstd

############################################
### Parameters

base_ds_fields = ['feature', 'parameter', 'method', 'product_code', 'owner', 'aggregation_statistic', 'frequency_interval', 'utc_offset']

base_attrs = {'station_id': {'cf_role': "timeseries_id", 'description': 'The unique ID associated with the geometry for a single result.'}, 'lat': {'standard_name': "latitude", 'units': "degrees_north"}, 'lon': {'standard_name': "longitude", 'units': "degrees_east"}, 'altitude': {'standard_name': 'surface_altitude', 'long_name': 'height above the geoid to the lower boundary of the atmosphere', 'units': 'm'}, 'geometry': {'long_name': 'The hexadecimal encoding of the Well-Known Binary (WKB) geometry', 'crs_EPSG': 4326}, 'station_geometry': {'long_name': 'The hexadecimal encoding of the Well-Known Binary (WKB) station geometry', 'crs_EPSG': 4326}, 'height': {'standard_name': 'height', 'long_name': 'vertical distance above the surface', 'units': 'm', 'positive': 'up'}, 'time': {'standard_name': 'time', 'long_name': 'start_time'}, 'name': {'long_name': 'station name'}, 'ref': {'long_name': 'station reference id given by the owner'}, 'modified_date': {'long_name': 'last modified date'}, 'band': {'long_name': 'band number'}, 'chunk_date': {'long_name': 'chunking date'}, 'chunk_day': {'long_name': 'chunking day', 'description': 'The chunk day is the number of days after 1970-01-01. Can be negative for days before 1970-01-01 with a minimum of -106751, which is 1677-09-22 (minimum possible date). The maximum value is 106751.'}, 'chunk_hash': {'long_name': 'chunk hash', 'description': 'The unique hash of the results parameter for comparison purposes.'}, 'chunk_id': {'long_name': 'chunk id', 'description': 'The unique id of the results chunk associated with the specific station.'}}

base_encoding = {'lon': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 0.0000001}, 'lat': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 0.0000001}, 'altitude': {'dtype': 'int32', '_FillValue': -9999, 'scale_factor': 0.001}, 'time': {'_FillValue': -99999999, 'units': "days since 1970-01-01 00:00:00"}, 'modified_date': {'_FillValue': -99999999, 'units': "days since 1970-01-01 00:00:00"}, 'band': {'dtype': 'int8', '_FillValue': -99}, 'chunk_day': {'dtype': 'int32'}, 'chunk_date': {'_FillValue': -99999999, 'units': "days since 1970-01-01 00:00:00"}}

ds_stn_file_str = '{ds_id}_{stn_id}_{date}.nc'
results_file_str = '{ds_id}_{version_date}_{stn_id}_{chunk_id}_{hash}_results.nc.zst'
stns_json_str = '{ds_id}_{version_date}_stations.json.zst'
rc_json_str = '{ds_id}_{version_date}_results_chunks.json.zst'
versions_json_str = '{ds_id}_versions.json.zst'
ds_json_str = '{ds_id}_dataset.json.zst'
dss_json_str = 'datasets.json.zst'

############################################
### Functions


# def write_nc_zstd(data: Union[xr.DataArray, xr.Dataset], output_path, retries=5):
#     """

#     """
#     counter = retries
#     while True:
#         try:
#             znc1 = write_pkl_zstd(data.to_netcdf())

#             source_checksum = zlib.adler32(znc1)

#             with open(output_path, 'wb') as f:
#                 f.write(output_path)

#             ## Test the write
#             with open(output_path, 'rb') as f:
#                 file_checksum = zlib.adler32(f.read())

#             if source_checksum == file_checksum:
#                 break
#             else:
#                 raise ValueError('checksum mismatch...')
#         except Exception as err:
#             print(str(err))
#             sleep(2)
#             counter = counter - 1
#             if counter <= 0:
#                 raise err


def extract_data_dimensions(data, parameter):
    """

    """
    data_index = data[parameter].dims
    vars2 = list(data.variables)
    vars3 = [v for v in vars2 if v not in data_index]

    vars_dict = {}
    for v in vars3:
        index1 = data[v].dims
        vars_dict[v] = index1

    ancillary_variables = [v for v, i in vars_dict.items() if (i == data_index) and (v != parameter)]

    main_vars = [parameter] + ancillary_variables

    return data_index, vars3, main_vars, ancillary_variables, vars_dict


def data_integrety_checks_v04(data, parameter, result_type, attrs, encoding, ancillary_variables):
    """

    """
    ## Check dims
    rt_dims_model = tdm.dataset.result_type_dict[result_type]
    _ = rt_dims_model(**data.dims)

    ## check data
    vars1 = {v: data[v].dtype.name for v in list(data.variables)}
    ts_essential_list = [parameter] + ancillary_variables

    ts_no_attrs_list = list(base_attrs.keys())

    attrs_keys = list(attrs.keys())
    for col in vars1:
        if not col in ts_no_attrs_list:
            if not col in ts_essential_list:
                if not col in attrs_keys:
                    raise ValueError(col + ' key is not in the attrs dict')

    for col, dtype in vars1.items():
        if not col in ts_no_attrs_list:
            if ('float' in dtype) or ('int' in dtype):
                if not col in encoding:
                    raise ValueError(col + ' must be in the encoding dict')


def add_metadata_results(results, metadata, version_date):
    """

    """
    md = copy.deepcopy(metadata)
    parameter = md['parameter']
    result_type = md['result_type']
    encoding = md['properties']['encoding']

    data_index, vars1, main_vars, ancillary_variables, vars_dict = extract_data_dimensions(results, parameter)

    if 'attrs' in md['properties']:
        attrs = md['properties']['attrs']
    else:
        attrs = {}

    for c, a in md['chunk_parameters'].items():
        md[c] = a

    param_attrs = tdm.dataset.ParameterAttrs(**md).dict(exclude_none=True)
    attrs[parameter] = param_attrs

    ## Checks
    data_integrety_checks_v04(results, parameter, result_type, attrs, encoding, ancillary_variables)

    ## Assign encodings
    encoding1 = copy.deepcopy(base_encoding)

    # Downcast height if possible
    results['height'] = pd.to_numeric(results['height'].values.round(3), downcast='integer')

    if 'int' in results['height'].dtype.name:
        height_enc = {'dtype': results['height'].dtype.name}
    elif 'float' in results['height'].dtype.name:
        height_enc = {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 0.001}
    else:
        raise TypeError('height should be either an int or a float')

    encoding1.update({'height': height_enc})

    # Add user-defined encodings
    for k, v in encoding.items():
        encoding1[k] = v

    # Add encodings
    for e, val in encoding1.items():
        if e in results:
            if ('dtype' in val) and (not 'scale_factor' in val):
                if 'int' in val['dtype']:
                    results[e] = results[e].astype(val['dtype'])
            if 'scale_factor' in val:
                precision = int(np.abs(np.log10(val['scale_factor'])))
                results[e] = results[e].round(precision)

            results[e].encoding = val

    ## Fix str encoding issue when the data type is object
    for v in vars1:
        if results[v].dtype.name == 'object':
            results[v] = results[v].astype(str)

    ## Add in metadata to results (must be done after all the data corrections)
    attrs1 = copy.deepcopy(base_attrs)

    for k, v in attrs.items():
        x = copy.deepcopy(v)
        for w in v:
            if isinstance(v[w], list):
                bool1 = all([isinstance(i, (int, float, str)) for i in v[w]])
                if bool1:
                    x[w] = ' '.join(v[w])
                else:
                    x.pop(w)
            elif not isinstance(v[w], (int, float, str)):
                x.pop(w)
        attrs1[k] = x

    if 'cf_standard_name' in attrs1[parameter]:
        attrs1[parameter]['standard_name'] = attrs1[parameter].pop('cf_standard_name')

    if len(ancillary_variables) > 0:
        attrs1[parameter].update({'ancillary_variables': ' '.join(ancillary_variables)})

    # Add final attributes
    for a, val in attrs1.items():
        if a in results:
            results[a].attrs = val

    ## Add top-level metadata
    title_str = '{agg_stat} {parameter} in {units} of the {feature} by a {method} owned by {owner}'.format(agg_stat=md['aggregation_statistic'], parameter=md['parameter'], units=md['units'], feature=md['feature'], method=md['method'], owner=md['owner'])

    results.attrs = {'result_type': result_type, 'title': title_str, 'institution': md['owner'], 'license': md['license'], 'source': md['method'], 'system_version': 4, 'version_date': pd.Timestamp(version_date).tz_localize(None).isoformat()}

    ## Test conversion to netcdf
    _ = results.to_netcdf()

    return results


def compare_dfs(old_df, new_df, on, parameter, add_old=False):
    """
    Function to compare two DataFrames with nans and return a dict with rows that have changed (diff), rows that exist in new_df but not in old_df (new), and rows  that exist in old_df but not in new_df (remove).
    Both DataFrame must have the same columns. If both DataFrames are identical, and empty DataFrame will be returned.

    Parameters
    ----------
    old_df : DataFrame
        The old DataFrame.
    new_df : DataFrame
        The new DataFrame.
    on : str or list of str
        The primary key(s) to index/merge the two DataFrames.
    parameter : str
        The parameter/column that should be compared.

    Returns
    -------
    DataFrame
        of the new dataset
    """
    if ~np.in1d(old_df.columns, new_df.columns).any():
        raise ValueError('Both DataFrames must have the same columns')

    # val_cols = [c for c in old_df.columns if not c in on]
    all_cols = new_df.columns.tolist()

    comp1 = pd.merge(old_df, new_df, on=on, how='outer', indicator=True, suffixes=('_x', ''))

    add_set = comp1.loc[comp1._merge == 'right_only', all_cols].copy()
    comp2 = comp1[comp1._merge == 'both'].drop('_merge', axis=1).copy()

    old_cols = list(on)
    old_cols_map = {c: c[:-2] for c in comp2 if '_x' in c}
    old_cols.extend(old_cols_map.keys())
    old_set = comp2[old_cols].copy()
    old_set.rename(columns=old_cols_map, inplace=True)
    new_set = comp2[all_cols].copy()

    isnull1 = new_set[parameter].isnull()
    if isnull1.any():
        new_set.loc[new_set[parameter].isnull(), parameter] = np.nan
    if old_set[parameter].dtype.type in (np.float32, np.float64):
        c1 = ~np.isclose(old_set[parameter], new_set[parameter], equal_nan=True)
    elif old_set[parameter].dtype.name == 'object':
        new_set[parameter] = new_set[parameter].astype(str)
        c1 = old_set[parameter].astype(str) != new_set[parameter]
    elif old_set[parameter].dtype.name == 'geometry':
        old1 = old_set[parameter].apply(lambda x: hash(x.wkt))
        new1 = new_set[parameter].apply(lambda x: hash(x.wkt))
        c1 = old1 != new1
    else:
        c1 = old_set[parameter] != new_set[parameter]
    notnan1 = old_set[parameter].notnull() | new_set[parameter].notnull()
    c2 = c1 & notnan1

    if (len(comp1) == len(comp2)) and (~c2).all():
        all_set = new_df
    else:
        diff_set = new_set[c2].copy()
        old_set2 = old_set[~c2].copy()

        if add_old:
            not_cols = list(on)
            [not_cols.extend([c]) for c in comp1.columns if '_x' in c]
            add_old1 = comp1.loc[comp1._merge == 'left_only', not_cols].copy()
            add_old1.rename(columns=old_cols_map, inplace=True)

            all_set = pd.concat([old_set2, diff_set, add_set, add_old1])
        else:
            all_set = pd.concat([old_set2, diff_set, add_set])

    return all_set


def compare_xrs(old_xr, new_xr, add_old=False):
    """

    """
    ## Determine the parameter to be compared and the dimensions
    vars1 = list(new_xr.variables)
    parameter = [v for v in vars1 if 'dataset_id' in new_xr[v].attrs][0]
    vars2 = [parameter]

    ## Determine if there are ancillary variables to pull through
    new_attrs = new_xr[parameter].attrs.copy()

    if 'ancillary_variables' in new_attrs:
        av1 = new_attrs['ancillary_variables'].split(' ')
        vars2.extend(av1)

    if not parameter in old_xr:
        raise ValueError(parameter + ' must be in old_xr')

    ## Reduce the dimensions for the comparison for compatibility
    new1_s = new_xr[vars2].squeeze()
    on = list(new1_s.dims)

    # Fix for when there is no dimension > 1
    if len(on) == 0:
        new1_s = new1_s.expand_dims('time')
        on = ['time']

    old1_s = old_xr[vars2].squeeze()
    old_on = list(old1_s.dims)
    if len(old_on) == 0:
        old1_s = old1_s.expand_dims('time')
        old_on = ['time']

    if not on == old_on:
        raise ValueError('Dimensions are not the same between the datasets')

    ## Assign variables
    keep_vars = on + vars2

    new_all_vars = list(new1_s.variables)
    new_bad_vars = [v for v in new_all_vars if not v in keep_vars]
    new2_s = new1_s.drop_vars(new_bad_vars)

    old_all_vars = list(old1_s.variables)
    old_bad_vars = [v for v in old_all_vars if not v in keep_vars]
    old2_s = old1_s.drop_vars(old_bad_vars)

    # Fix datetime rounding issues...
    for v in list(old2_s.variables):
        if old2_s[v].dtype.name == 'datetime64[ns]':
            old2_s[v] = old2_s[v].dt.round('s')

    for v in list(new2_s.variables):
        if new2_s[v].dtype.name == 'datetime64[ns]':
            new2_s[v] = new2_s[v].dt.round('s')

    ## Pull out data for comparison
    old_df = old2_s.to_dataframe().reset_index()
    new_df = new2_s.to_dataframe().reset_index()

    ## run comparison
    comp = compare_dfs(old_df, new_df, on, parameter, add_old=add_old)

    if comp.empty:
        # print('Nothing has changed. Returning empty DataFrame.')
        return comp

    else:

        ## Fix NaT mod dates
        if 'modified_date' in comp:
            run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)
            comp.loc[comp['modified_date'].isnull(), 'modified_date'] = run_date

        ## Repackage into netcdf
        comp2 = comp.set_index(list(on)).sort_index().to_xarray()

        # Fix datetime rounding issues...
        for v in list(comp2.variables):
            if comp2[v].dtype.name == 'datetime64[ns]':
                comp2[v] = comp2[v].dt.round('s')

        for v in vars1:
            if v not in vars2:
                if v not in on:
                    comp2[v] = new_xr[v].copy()
                comp2[v].attrs = new_xr[v].attrs.copy()
                comp2[v].encoding = new_xr[v].encoding.copy()

        new_dims = new_xr[parameter].dims
        dim_dict = dict(comp2.dims)
        data_shape = tuple(dim_dict[d] for d in new_dims)

        for v in vars2:
            comp2 = comp2.assign({v: (new_dims, comp2[v].values.reshape(data_shape))})
            comp2[v].attrs = new_xr[v].attrs.copy()
            comp2[v].encoding = new_xr[v].encoding.copy()

        comp2.attrs = new_xr.attrs.copy()
        comp2.encoding = new_xr.encoding.copy()

        return comp2


def update_compare_results(previous_result, metadata, version_date, new_path):
    """

    """
    parts1 = previous_result.parts
    ds_id = parts1[-3]
    stn_id = parts1[-2]
    chunk_id = parts1[-1].split('.')[0]

    version_date_key = make_run_date_key(version_date)

    glob_str = '{ds_id}_{vd}_{stn_id}_{chunk_id}_*_results.nc.zst'.format(ds_id=ds_id, stn_id=stn_id, chunk_id=chunk_id, vd=version_date_key)
    new_results = glob.glob(os.path.join(new_path, glob_str))

    old_xr = xr.load_dataset(previous_result)

    if not new_results:
        old_xr.attrs['version_date'] = pd.Timestamp(version_date).tz_localize(None).isoformat()

        up1 = old_xr

        hash_id = up1.chunk_hash.values.flatten()[0]

        new_result_path = os.path.join(new_path, '{ds_id}_{vd}_{stn_id}_{chunk_id}_{hash_id}_results.nc.zst'.format(ds_id=ds_id, stn_id=stn_id, chunk_id=chunk_id, vd=version_date_key, hash_id=hash_id))

    else:
        new_result_path = new_results[0]

        new_xr = xr.load_dataset(utils.read_pkl_zstd(new_result_path))

        dims = new_xr.dims

        if ('modified_date' in new_xr) or ('geometry' in dims):
            # if ('modified_date' in new_xr) and ('modified_date' not in old_xr):
            #     run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)
            #     dims = new_xr.dims
            #     mod_date_dims = {d: dims[d] for d in new_xr['modified_date'].dims}
            #     old_xr['modified_date'] = run_date
            #     old_xr['modified_date'] = new_xr[['modified_date']].expand_dims(mod_date_dims)
            #     old_xr = old_xr.assign({'modified_date': (tuple(mod_date_dims), new_xr['modified_date'].expand_dims(mod_date_dims).data)})
            #     old_xr['modified_date'].attrs = new_xr['modified_date'].attrs
            #     old_xr['modified_date'].encoding = new_xr['modified_date'].encoding

            # elif ('modified_date' not in new_xr) and ('modified_date' in old_xr):
            #     old_xr = old_xr.drop('modified_date')

            up1 = compare_xrs(old_xr, new_xr, True)
        # elif 'geometry' in dims:
        #     if dims['geometry'] == 1:
        #         geometry = new_xr.geometry.values[0]
        #         up1 = new_xr.squeeze('geometry').combine_first(old_xr.squeeze('geometry'))
        #         up1 = up1.assign_coords(geometry=geometry)
        #         up1['geometry'] = up1['geometry'].astype(str)
        #         up1 = up1.expand_dims('geometry')
        #     else:
        #         raise NotImplementedError('Combining results with multiple geometries is not currently supported.')
        else:
            up1 = new_xr.combine_first(old_xr)

        new_xr.close()
        del new_xr

    write_pkl_zstd(up1.to_netcdf(), new_result_path)

    ## Save new results
    results_new_paths = save_new_results(new_result_path, metadata, version_date, overwrite=True)
    results_new_path = results_new_paths[0]

    ## Remove old files and objects
    os.remove(previous_result)

    old_xr.close()
    del old_xr
    up1.close()
    del up1

    return results_new_path


def read_result_chunk_data(path):
    """

    """
    len1 = os.path.getsize(path)

    data = xr.load_dataset(utils.read_pkl_zstd(path))
    results_chunk_dict = get_result_chunk_data(data)

    results_chunk_dict.update({'content_length': len1})

    chunk_m = tdm.dataset.ResultChunk(**results_chunk_dict)

    chunk_dict = orjson.loads(chunk_m.json(exclude_none=True))

    return chunk_dict


def update_results_chunks(data_paths, new_path, old_rc_data=None, max_workers=1):
    """
    The data_paths should contain all of the paths for a single dataset.
    """
    ds_id, version_date_key, _, _, _, _ = os.path.split(data_paths[0])[1].split('_')

    if isinstance(old_rc_data, list):
        rc_dict = {}
        for rc in old_rc_data:
            chunk_id = rc['chunk_id']
            stn_id = rc['station_id']
            if stn_id in rc_dict:
                rc_dict[stn_id][chunk_id] = rc
            else:
                rc_dict.update({stn_id: {chunk_id: rc}})
    else:
        rc_dict = {}

    ## Get the results chunk data
    # chunks_list = []
    # append = chunks_list.append
    # for path in data_paths:
    #     c = read_result_chunk_data(path)
    #     append(c)

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for path in data_paths:
            f = executor.submit(read_result_chunk_data, path)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    chunks_list = [r.result() for r in runs[0]]

    for chunk in chunks_list:
        chunk_id = chunk['chunk_id']
        stn_id = chunk['station_id']

        if stn_id in rc_dict:
            rc_dict[stn_id][chunk_id] = chunk
        else:
            rc_dict.update({stn_id: {chunk_id: chunk}})

    ## Make into single list for json
    rc_list = []
    extend = rc_list.extend
    for stn_id, chunk in rc_dict.items():
        extend(list(chunk.values()))

    ## Make the final rc object
    rc_file_name = rc_json_str.format(ds_id=ds_id, version_date=version_date_key)
    rc_file_path = os.path.join(new_path, rc_file_name)

    write_json_zstd(rc_list, rc_file_path)

    return rc_file_path


def read_station_data_from_xr(path):
    """

    """
    data = xr.load_dataset(utils.read_pkl_zstd(path))
    stn_data = get_station_data_from_xr(data)

    return stn_data


def update_stations(data_paths, rc_path, new_path, old_stns_data=None, max_workers=1):
    """
    The data_paths should contain all of the paths for a single dataset.
    """
    ds_id, version_date_key, _, _, _, _ = os.path.split(data_paths[0])[1].split('_')

    ## Process results chunks data
    rc_list = utils.read_json_zstd(rc_path)

    rc_dict = {}
    for rc in rc_list:
        stn_id = rc['station_id']
        if stn_id in rc_dict:
            rc_dict[stn_id].append(rc)
        else:
            rc_dict[stn_id] = [rc]

    ## Read in old stns data
    if isinstance(old_stns_data, list):
        stns_dict = {}
        for stn in old_stns_data:
            stn_id = stn['station_id']
            stns_dict[stn_id] = stn
    else:
        stns_dict = {}

    ## Prepare the paths into dicts
    path_dict = {}
    for path in data_paths:
        ds_id, version_date_key, stn_id, _, _, _ = os.path.split(path)[1].split('_')
        path_dict[stn_id] = path

    ## Run through each station
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for stn_id, path in path_dict.items():
            f = executor.submit(read_station_data_from_xr, path)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    stn_data_list = [r.result() for r in runs[0]]

    for stn_data in stn_data_list:
        stn_id = stn_data['station_id']
        height = int(stn_data['heights'][0] * 1000)

        stn_rc_list = rc_dict[stn_id]

        n_times = 0
        content_len = 0
        heights = set()
        from_dates = []
        to_dates = []

        for c in stn_rc_list:
            c_height = c['height']
            content_len = content_len + c['content_length']
            heights.add(round(c_height*0.001, 3))
            from_dates.append(c['from_date'])
            to_dates.append(c['to_date'])

            if c_height == height:
                n_times = n_times + c['n_times']

        from_date1 = pd.to_datetime(from_dates).min()
        to_date1 = pd.to_datetime(to_dates).max()
        heights1 = list(heights)
        heights1.sort()

        ## Append to stn data
        stn_data['dimensions']['time'] = n_times
        stn_data['dimensions']['height'] = len(heights1)
        stn_data['time_range']['from_date'] = from_date1
        stn_data['time_range']['to_date'] = to_date1
        stn_data['heights'] = heights1
        stn_data['content_length'] = content_len

        stn_data1 = orjson.loads(tdm.dataset.Station(**stn_data).json(exclude_none=True))

        stns_dict[stn_id] = stn_data1

    ## Make into single list for json
    stns_list = list(stns_dict.values())

    ## Make the final object
    stns_file_name = stns_json_str.format(ds_id=ds_id, version_date=version_date_key)
    stns_file_path = os.path.join(new_path, stns_file_name)

    write_json_zstd(stns_list, stns_file_path)

    return stns_file_path


def update_versions(version_data, new_path, old_versions=None):
    """

    """
    ## Check version_dict data model
    version_dict1 = tdm.dataset.ResultVersion(**version_data).dict(exclude_none=True)

    ## Process versions
    if isinstance(old_versions, list):
        exists = any([version_dict1['version_date'].isoformat() == v['version_date'] for v in old_versions])

        if exists:
            version_list = []
            for v in old_versions:
                if version_dict1['version_date'].isoformat() == v['version_date']:
                    version_list.append(version_dict1)
                else:
                    version_list.append(v)
        else:
            version_list = old_versions.copy()
            version_list.append(version_dict1)
    else:
        version_list = [version_dict1]

    ## Save to file
    dataset_id = version_dict1['dataset_id']

    v_file_name = versions_json_str.format(ds_id=dataset_id)
    v_file_path = os.path.join(new_path, v_file_name)

    write_json_zstd(version_list, v_file_path)

    return v_file_path


def update_dataset(dataset, new_path, stns_path, system_version):
    """

    """
    dataset_id = dataset['dataset_id']

    ## Get the stations agg
    stns = utils.read_json_zstd(stns_path)

    ## generate stats for the dataset metadata
    ds_stats = stats_for_dataset_metadata(stns)

    if dataset['result_type'] == 'time_series':
        if 'spatial_resolution' in ds_stats:
            ds_stats.pop('spatial_resolution')

    dataset.update(ds_stats)

    ## Add version number
    dataset.update({'system_version': system_version})

    ## Check and create dataset metadata
    ds4 = tdm.dataset.Dataset(**dataset)

    ds5 = orjson.loads(ds4.json(exclude_none=True))

    ## Write the object
    ds_path = os.path.join(new_path, ds_json_str.format(ds_id=dataset_id))
    write_json_zstd(ds5, ds_path)

    return ds_path


def update_dataset_agg(ds_paths, new_path, old_datasets=None):
    """

    """
    ## Read in old datasets
    if isinstance(old_datasets, list):
        ds_dict = {}
        for ds in old_datasets:
            ds_id = ds['dataset_id']
            if ds_id in ds_dict:
                raise ValueError('There are two datasets with the same dataset_id...we have got a problem...')
            ds_dict[ds_id] = ds
    else:
        ds_dict = {}

    ## Update datasets
    for path in ds_paths:
        ds = utils.read_json_zstd(path)
        ds_id = ds['dataset_id']
        ds_dict[ds_id] = ds

    ds_list = list(ds_dict.values())

    ## Write the object
    dss_path = os.path.join(new_path, dss_json_str)
    write_json_zstd(ds_list, dss_path)

    return dss_path


def prepare_file_for_s3(path, s3, bucket, system_version=4):
    """

    """
    run_date_key = make_run_date_key()

    content_type = 'application/json'

    ## Determine which kind of file it is
    file_name = os.path.split(path)[1]

    if file_name.endswith('results.nc.zst'):
        ds_id, version_date_key, stn_id, chunk_id, chunk_hash, _ = file_name.split('_')

        key_name = tdm.utils.key_patterns[system_version]['results'].format(dataset_id=ds_id, version_date=version_date_key, station_id=stn_id, chunk_id=chunk_id)

        metadata = {'run_date': run_date_key, 'dataset_id': ds_id, 'version_date': version_date_key, 'station_id': stn_id, 'chunk_id': chunk_id, 'chunk_hash': chunk_hash}
        content_type = 'application/netcdf'
    elif file_name.endswith('results_chunks.json.zst'):
        ds_id, version_date_key, _, _ = file_name.split('_')

        key_name = tdm.utils.key_patterns[system_version]['results_chunks'].format(dataset_id=ds_id, version_date=version_date_key)

        metadata = {'run_date': run_date_key, 'dataset_id': ds_id, 'version_date': version_date_key}
    elif file_name.endswith('stations.json.zst'):
        ds_id, version_date_key, _ = file_name.split('_')

        key_name = tdm.utils.key_patterns[system_version]['stations'].format(dataset_id=ds_id, version_date=version_date_key)

        metadata = {'run_date': run_date_key, 'dataset_id': ds_id, 'version_date': version_date_key}
    elif file_name.endswith('dataset.json.zst'):
        ds_id, _ = file_name.split('_')

        key_name = tdm.utils.key_patterns[system_version]['dataset'].format(dataset_id=ds_id)

        metadata = {'run_date': run_date_key, 'dataset_id': ds_id}
    elif file_name.endswith('versions.json.zst'):
        ds_id, _ = file_name.split('_')

        key_name = tdm.utils.key_patterns[system_version]['versions'].format(dataset_id=ds_id)

        metadata = {'run_date': run_date_key, 'dataset_id': ds_id}
    elif file_name.endswith('datasets.json.zst'):
        key_name = tdm.utils.key_patterns[system_version]['datasets']

        metadata = {'run_date': run_date_key}
    else:
        raise ValueError('The file passed is not acceptable.')

    ## Make the parameter dict
    dict1 = {'s3': s3, 'bucket': bucket, 'file_path': path, 'key': key_name, 'metadata': metadata, 'content_type': content_type}

    return dict1


def assign_ds_ids(datasets):
    """
    Parameters
    ----------
    datasets : list
    """
    dss = copy.deepcopy(datasets)

    ### Iterate through the dataset list
    for ds in dss:
        # print(ds)
        ## Validate base model
        _ = tdm.dataset.DatasetBase(**ds)

        base_ds = {k: ds[k] for k in base_ds_fields}
        base_ds_b = orjson.dumps(base_ds, option=orjson.OPT_SERIALIZE_NUMPY)
        ds_id = blake2b(base_ds_b, digest_size=12).hexdigest()

        ds['dataset_id'] = ds_id

        ## Validate full model
        _ = tdm.dataset.Dataset(**ds)

    return dss


def assign_chunk_id(chunk_dict):
    """
    Parameters
    ----------
    chunk_dict : dict
        With keys of station_id, heights_index, and start_date. See the ChunkID data model/class for more details.
    """
    chunk_json = tdm.dataset.ChunkID(**chunk_dict).json(exclude_none=True).encode('utf-8')
    chunk_id = blake2b(chunk_json, digest_size=12).hexdigest()

    return chunk_id


def process_datasets(datasets):
    """

    """
    if isinstance(datasets, dict):
        dataset_list = []
        for ht_ds, ds_list in datasets.items():
            if isinstance(ds_list, list):
                ds_list2 = assign_ds_ids(ds_list)
            elif isinstance(ds_list, dict):
                ds_list2 = assign_ds_ids([ds_list])

            datasets[ht_ds] = ds_list2

        [dataset_list.extend(ds_list) for ht_ds, ds_list in datasets.items()]
    elif isinstance(datasets, list):
        dataset_list = assign_ds_ids(datasets)
    else:
        raise TypeError('datasets must be either a dict or list.')

    return dataset_list


def create_geometry_df(df, extent=False, altitude=False, to_wkb_hex=True, precision=7, check_geometries=True):
    """

    """
    if extent:
        if ('lon' in df) and ('lon' in df):
            min_lon = round(df['lon'].min(), precision)
            max_lon = round(df['lon'].max(), precision)
            min_lat = round(df['lat'].min(), precision)
            max_lat = round(df['lat'].max(), precision)
            geometry = pd.Series(box(min_lon, min_lat, max_lon, max_lat))
            # geometry = shape(geojson.Polygon([[(min_lon, min_lat), (min_lon, max_lat), (max_lon, max_lat), (max_lon, min_lat), (min_lon, min_lat)]], True, precision=precision))
        else:
            raise ValueError('Extent must have lat and lon in the df.')
    else:
        if 'geometry' in df:
            geometry = df['geometry']
        elif ('lon' in df) and ('lon' in df):
            if altitude:
                if 'altitude' in df:
                    coords = df.apply(lambda x: (round(x.lon, precision), round(x.lat, precision), x.altitude), axis=1)
                else:
                    coords = df.apply(lambda x: (round(x.lon, precision), round(x.lat, precision)), axis=1)
            else:
                coords = df.apply(lambda x: (round(x.lon, precision), round(x.lat, precision)), axis=1)
            geometry = coords.apply(lambda x: Point(x))
            # geometry = coords.apply(lambda x: shape(geojson.Point(x, True, precision=precision)))
        else:
            raise ValueError('Either a dict of geometry or a combo of lat and lon must be in the dataframe.')

        ## Check if geometries are valid (according to shapely)
        if check_geometries:
            for g in geometry:
                if not g.is_valid:
                    raise ValueError(str(g) + ': This shapely geometry is not valid')

    if to_wkb_hex:
        geometry = geometry.apply(lambda x: x.wkb_hex)

    return geometry


def assign_station_id(geometry):
    """
    Parameters
    ----------
    geoemtry : shapely geometry class
    """
    geo = wkt.loads(wkt.dumps(geometry, rounding_precision=5))
    station_id = blake2b(geo.wkb, digest_size=12).hexdigest()

    return station_id


def assign_station_ids_df(stns_df, extent=False):
    """

    """
    geometry = create_geometry_df(stns_df, extent=extent, altitude=False, to_wkb_hex=False)

    stn_ids = geometry.apply(lambda x: assign_station_id(x))

    return stn_ids


def process_sparse_stations_from_df(stns, precision=7):
    """
    Function that takes a stns dataframe of station data and converts it to an Xarray Dataset for Tethys. This is ultimately meant to be combined with the time series data for futher processing. If a geometry column is provided, it must be as a geojson-type dict (not a geopandas column).

    """
    stns2 = stns.copy()

    ## Assign geometries
    stns2['geometry'] = create_geometry_df(stns2, to_wkb_hex=True, precision=precision)

    ## Final station processing
    stns3 = stns2.drop(['lat', 'lon'], axis=1).set_index('geometry')

    stns4 = stns3.to_xarray()

    return stns4


def stations_dict_to_df(stns):
    """

    """
    s1 = copy.deepcopy(stns)

    ## Get rid of unnecessary stuff
    _ = [s.pop('stats') for s in s1 if 'stats' in s]
    _ = [s.pop('virtual_station') for s in s1 if 'virtual_station' in s]
    _ = [s.pop('modified_date') for s in s1 if 'modified_date' in s]
    _ = [s.pop('dataset_id') for s in s1 if 'dataset_id' in s]
    _ = [s.pop('content_length') for s in s1 if 'content_length' in s]
    _ = [s.pop('heights') for s in s1 if 'heights' in s]
    _ = [s.pop('time_range') for s in s1 if 'time_range' in s]
    _ = [s.pop('dimensions') for s in s1 if 'dimensions' in s]
    _ = [s.pop('bands') for s in s1 if 'bands' in s]

    ## Process attrs
    attrs = {}
    for s in s1:
        s['lon'] = s['geometry']['coordinates'][0]
        s['lat'] = s['geometry']['coordinates'][1]
        s.pop('geometry')
        if 'properties' in s:
            if s['properties']:
                for pk, pv in s['properties'].items():
                    attrs.update({pk: pv['attrs']})
                    if isinstance(pv['data'], list):
                        s.update({pk: pv['data'][0]})
                    else:
                        s.update({pk: pv['data']})
            s.pop('properties')

    ## Convert to df
    s2 = pd.DataFrame(s1)

    ## Process geometry
    s2['geometry'] = create_geometry_df(s2, to_wkb_hex=True, precision=7)

    ## Return
    return s2, attrs


def combine_obs_stn_data(ts_data, stn_data, mod_date=False):
    """
    Function to take a time series DataFrame and station data (in 3 formats) and combine them into a single xr.Dataset.

    Parameters
    ----------
    ts_data: pd.DataFrame
        The DataFrame should have height and time as columns in addition to the parameter column.
    stn_data: pd.Series, pd.DataFrame, dict, xr.Dataset
        The station data that should have geometry as a column.
    mod_date: bool
        The the modified_date be added to the ts_data?

    Returns
    -------
    xr.Dataset
    """
    if isinstance(stn_data, pd.Series):
        stn = stn_data.to_frame().T.set_index('geometry').to_xarray()
    elif isinstance(stn_data, pd.DataFrame):
        stn = stn_data.set_index('geometry').to_xarray()
    elif isinstance(stn_data, dict):
        stn = pd.DataFrame([stn_data]).set_index('geometry').to_xarray()
    else:
        stn = stn_data

    if ts_data.empty:
        raise ValueError('ts_data is empty.')

    if 'time' not in ts_data.columns:
        raise ValueError('The time column is not in ts_data.')

    if 'height' not in ts_data.columns:
        raise ValueError('The height column is not in ts_data.')

    obs2 = ts_data.copy()

    obs2['geometry'] = stn['geometry'].values[0]

    obs2.set_index(['time', 'geometry', 'height'], inplace=True)

    if mod_date:
        mod_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)
        obs2['modified_date'] = mod_date

    obs3 = obs2.to_xarray()
    obs4 = xr.combine_by_coords([obs3, stn], data_vars='minimal')

    return obs4


# def get_new_stats(data):
#     """

#     """
#     vars1 = list(data.variables)
#     parameter = [v for v in vars1 if 'dataset_id' in data[v].attrs][0]

#     encoding = data[parameter].encoding.copy()

#     if 'scale_factor' in encoding:
#         precision = int(np.abs(np.log10(data[parameter].encoding['scale_factor'])))
#     else:
#         precision = 0

#     data1 = data[parameter]

#     min1 = round(float(data1.min()), precision)
#     max1 = round(float(data1.max()), precision)
#     mean1 = round(float(data1.mean()), precision)
#     median1 = round(float(data1.median()), precision)
#     count1 = int(data1.count())

#     stats1 = tdm.dataset.Stats(min=min1, max=max1, mean=mean1, median=median1, count=count1)

#     return stats1


def get_station_data_from_xr(data):
    """
    Parameters
    ----------
    data : xr.Dataset
    """
    vars1 = [v for v in list(data.variables) if 'chunk' not in v]
    dims0 = dict(data.dims)
    dims1 = list(dims0.keys())
    parameter = [v for v in vars1 if 'dataset_id' in data[v].attrs][0]
    attrs = data[parameter].attrs.copy()
    data_vars = [parameter]
    if 'ancillary_variables' in attrs:
        ancillary_variables = attrs['ancillary_variables'].split(' ')
        data_vars.extend(ancillary_variables)

    stn_fields = list(tdm.dataset.Station.schema()['properties'].keys())

    ## Geometry
    if 'station_geometry' in dims1:
        geo1 = mapping(wkb.loads(data['station_geometry'].values[0], True))
    elif 'geometry' in dims1:
        geo1 = mapping(wkb.loads(data['geometry'].values[0], True))
    else:
        lon = data['lon'].values[0]
        lat = data['lat'].values[0]
        geo1 = geojson.Point([lon, lat], True, 7)

    stn_fields.remove('geometry')

    lat_lon = ['lon', 'lat']

    stn_vars = [v for v in vars1 if (not v in dims1) and (not v in data_vars) and (not v in lat_lon)]
    if ('geometry' in dims1) or ('station_geometry' in dims1):
        stn_data1 = {k: v['data'][0] for k, v in data[stn_vars].to_dict()['data_vars'].items() if k in stn_fields}
        props = {s: {'data': data[s].to_dict()['data'][0], 'attrs': data[s].to_dict()['attrs']} for s in stn_vars if s not in stn_fields}
    else:
        stn_data1 = {k: v['data'][0][0] for k, v in data[stn_vars].to_dict()['data_vars'].items() if k in stn_fields}
        props = {s: {'data': data[s].to_dict()['data'][0][0], 'attrs': data[s].to_dict()['attrs']} for s in stn_vars if s not in stn_fields}
    stn_data1.update({'geometry': geo1})
    if 'altitude' in stn_data1:
        stn_data1['altitude'] = round(stn_data1['altitude'], 3)
    # if not 'virtual_station' in stn_data1:
    #     stn_data1['virtual_station'] = False

    stn_data1['dimensions'] = dims0
    stn_data1['heights'] = data['height'].values.tolist()

    from_date = pd.Timestamp(data['time'].min().values).tz_localize(None)
    to_date = pd.Timestamp(data['time'].max().values).tz_localize(None)

    stn_data1['time_range'] = {'from_date': from_date, 'to_date': to_date}
    stn_data1['dataset_id'] = attrs['dataset_id']

    stn_data1['modified_date'] = pd.Timestamp.now('UTC').tz_localize(None).round('S')

    ## get the stats
    # stats1 = get_new_stats(data)
    # stn_data1['stats'] = stats1

    if props:
        stn_data1['properties'] = props

    ## Check model
    stn_m = tdm.dataset.Station(**stn_data1)

    return orjson.loads(stn_m.json(exclude_none=True))


def stats_for_dataset_metadata(stns):
    """
    I need time_range, extent, and if grid the spatial_resolution.
    """
    dict1 = {}
    ## spatial resolution
    if 'lat' in stns[0]['dimensions']:
        lat_dim = int(np.median([s['dimensions']['lat'] for s in stns]))

        type1 = stns[0]['geometry']['type']

        if type1 in ['Polygon', 'Line']:
            geo = [s['geometry']['coordinates'][0][0][-1] for s in stns]
        else:
            geo = [s['geometry']['coordinates'][-1] for s in stns]

        geo1 = np.unique(np.array(geo).round(5))
        geo1.sort()
        diff1 = np.diff(geo1)
        res1 = round(np.median(diff1)/lat_dim, 5)

        dict1.update({'spatial_resolution': res1})

    ## Extent
    geo = np.array([s['geometry']['coordinates'] for s in stns]).round(5)

    len1 = int(np.prod(geo.shape)/2)
    geo1 = geo.T.reshape(2, len1)
    min_lon, min_lat = geo1.min(axis=1)
    max_lon, max_lat = geo1.max(axis=1)

    extent1 = mapping(box(min_lon, min_lat, max_lon, max_lat))

    dict1.update({'extent': extent1})

    ## time range
    trange1 = np.array([[s['time_range']['from_date'], s['time_range']['to_date']] for s in stns])
    mins, maxes = trange1.T

    min_t = min(mins)
    max_t = max(maxes)

    dict1.update({'time_range': {'from_date': min_t, 'to_date': max_t}})

    ## Heights
    heights1 = []
    _ = [heights1.extend(s['heights']) for s in stns]
    heights2 = list(set(heights1))
    heights2.sort()

    dict1.update({'heights': heights2})

    return dict1


def preprocess_data_structure(nc_path, time_name, x_name, y_name, variables, time_index_bool=None, projected_coordinates=True):
    """

    """
    new_paths = []
    base_dims = (time_name, y_name, x_name)
    xr1 = xr.open_dataset(nc_path)

    ## Remove time duplicates if necessary
    if time_index_bool is not None:
        xr1 = xr1.sel(time=time_index_bool)

    ## Get first timestamp for file naming
    time1 = pd.Timestamp(xr1[time_name].values[0])
    time1_str = time1.strftime('%Y%m%d%H%M%S')

    ## Iterate through variables
    for v in variables:
        xr2 = xr1[v].copy().load()
        dims = xr2.dims
        height_name_list = list(set(dims).difference(set(base_dims)))
        if len(height_name_list) > 1:
            shape1 = xr2.shape
            height_name_list = []
            for i, d in enumerate(dims):
                if d not in base_dims:
                    shape2 = shape1[i]
                    if shape2 > 1:
                        height_name_list.append(d)
            if len(height_name_list) > 1:
                raise ValueError('Variable has more than 4 dimensions! What kind of data is this!?')

        ## Transpose, sort, and rename
        if len(height_name_list) == 1:
            height_name = height_name_list[0]
            xr2 = xr2.transpose(time_name, y_name, x_name, height_name)
            xr2 = xr2.rename({time_name: 'time', height_name: 'height'}).sortby(['time', y_name, x_name, 'height'])
        else:
            xr2 = xr2.transpose(time_name, y_name, x_name)
            xr2 = xr2.rename({time_name: 'time'}).sortby(['time', y_name, x_name])

        if projected_coordinates:
            xr2 = xr2.rename({x_name: 'x', y_name: 'y'})
            new_file_name_str = '{var}_proj_{date}.nc'
        else:
            xr2 = xr2.rename({x_name: 'lon', y_name: 'lat'})
            new_file_name_str = '{var}_wgs84_{date}.nc'

        ## Save data
        path1 = pathlib.Path(nc_path)
        base_path = path1.parent
        new_file_name = new_file_name_str.format(var=v, date=time1_str)
        new_path = base_path.joinpath(new_file_name)
        xr2.to_netcdf(new_path, unlimited_dims=['time'])
        new_paths.append(str(new_path))

        xr2.close()
        del xr2

    xr1.close()
    del xr1

    ## delete old file
    os.remove(nc_path)

    return new_paths


def resample_to_wgs84_grid(nc_path, proj4_crs, grid_res, order=2, min_val=None, max_val=None, bbox=None, time_name='time', x_name='x', y_name='y', save_data=True):
    """

    """
    new_file_name_str = '{var}_wgs84_{date}.nc'
    nc_path1 = pathlib.Path(nc_path)
    file_name = nc_path1.stem
    var, date = file_name.split('_proj_')

    data = xr.open_dataset(nc_path)
    coords = list(data.coords)
    encoding = data[var].encoding.copy()
    data[var] = data[var].astype(float)

    if 'height' in coords:
        grp1 = data.groupby('height')

        xr_list = []

        for h, g in grp1:
            g1 = g.copy().load()

            i1 = Interp(grid_data=g1, grid_time_name=time_name, grid_x_name=x_name, grid_y_name=y_name, grid_data_name=var, grid_crs=proj4_crs)

            new_grid = i1.grid_to_grid(grid_res, 4326, order=order, bbox=bbox)
            if isinstance(min_val, (int, float)):
                new_grid = xr.where(new_grid.precip <= min_val, min_val, new_grid.precip)
            if isinstance(max_val, (int, float)):
                new_grid = xr.where(new_grid.precip >= max_val, max_val, new_grid.precip)

            new_grid3 = new_grid.rename({x_name: 'lon', y_name: 'lat', 'precip': var})
            new_grid3 = new_grid3.assign_coords(height=h).expand_dims('height')

            xr_list.append(new_grid3)

            g1.close()
            del g1

        new_grid4 = xr.combine_by_coords(xr_list).transpose('time', 'lat', 'lon', 'height')

    else:
        g1 = data.copy().load()

        i1 = Interp(grid_data=g1, grid_time_name=time_name, grid_x_name=x_name, grid_y_name=y_name, grid_data_name=var, grid_crs=proj4_crs)

        new_grid = i1.grid_to_grid(grid_res, 4326, order=order, bbox=bbox)
        if isinstance(min_val, (int, float)):
            new_grid = xr.where(new_grid.precip <= min_val, min_val, new_grid.precip)
        if isinstance(max_val, (int, float)):
            new_grid = xr.where(new_grid.precip >= max_val, max_val, new_grid.precip)

        new_grid4 = new_grid.rename({x_name: 'lon', y_name: 'lat', 'precip': var}).transpose('time', 'lat', 'lon')


        g1.close()
        del g1

    data.close()
    del data

    new_grid4[var].encoding = encoding

    # if isinstance(bbox, tuple):
    #     new_grid4 = new_grid4.sel(lon=slice(bbox[0], bbox[1]), lat=slice(bbox[2], bbox[3]))

    if save_data:
        new_file_name = new_file_name_str.format(var=var, date=date)
        new_path = nc_path1.parent.joinpath(new_file_name)
        new_grid4.to_netcdf(new_path, unlimited_dims=['time'])
        os.remove(nc_path)

        new_grid4.close()
        del new_grid4

        return str(new_path)

    else:
        return new_grid4


def calc_new_variable(path_dict, dataset, version_date, variables, func, out_path):
    """

    """
    paths = [v for k, v in path_dict.items() if k in variables]

    # Load in the required data and calc the new dataset variable
    data_list = [xr.open_dataset(p) for p in paths]
    data = xr.merge(data_list)
    results = func(data).copy().load()
    results.name = dataset['parameter']
    results = results.to_dataset()

    # Add in the dataset metadata
    results = add_metadata_results(results, dataset, version_date)

    # Remove encodings for height, lat, and lon...because CDO...
    for v in ['lat', 'lon', 'height']:
        if v in results:
            results[v].encoding = {}

    # Save results
    file_name = out_path.stem
    date = file_name.split('_wgs84_')[1]

    new_file_name = '{ds_id}_{date}.nc'.format(ds_id=dataset['dataset_id'], date=date)
    new_path = out_path.parent.joinpath(new_file_name)
    results.to_netcdf(new_path, unlimited_dims=['time'])

    data.close()
    del data
    results.close()
    del results

    return str(new_path)


def calc_new_variables(nc_paths, dataset_codes_dict, version_date, func_dict):
    """

    """
    path_dict = {pathlib.Path(p).stem.split('_wgs84_')[0]: p for p in nc_paths}
    out_path = pathlib.Path(nc_paths[0])

    ## Iterate through the datasets
    new_paths = []
    for ds_code, dataset in dataset_codes_dict.items():
        # print(ds_code)
        func1 = func_dict[ds_code]
        func = func1['function']
        variables = func1['variables']
        path1 = calc_new_variable(path_dict, dataset, version_date, variables, func, out_path)
        new_paths.append(path1)

    # TODO: need to figure out how to do this in a multiprocessing way...
    # Passing a function seems to cause it to stall...

    # with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
    #     futures = []
    #     for ds_code, dataset in datasets_dict.items():
    #         # print(ds_code)
    #         func1 = func_dict[ds_code]
    #         func = func1['function']
    #         variables = func1['variables']
    #         f = executor.submit(calc_new_variable, path_dict, dataset, version_date, variables, func, out_path)
    #         futures.append(f)
    #     runs = concurrent.futures.wait(futures)

    # # process output
    # new_paths = [r.result() for r in runs[0]]

        # # Get input parameters and functions
        # results1 = calc_new_variable(path_dict, d, func_dict)

        # # Add in the dataset metadata
        # results2 = add_metadata_results(results1, d, version_date)

        # # Remove encodings for height, lat, and lon...because CDO...
        # for v in ['lat', 'lon', 'height']:
        #     if v in results2:
        #         results2[v].encoding = {}

        # # Save results
        # new_file_name = new_file_name_str.format(ds_id=d['dataset_id'], date=date)
        # new_path = path1.parent.joinpath(new_file_name)
        # results2.to_netcdf(new_path, unlimited_dims=['time'])

        # # Clean up
        # results1.close()
        # del results1
        # results2.close()
        # del results2

        # new_paths.append(str(new_path))

    for p in nc_paths:
        os.remove(p)

    return new_paths


def calc_null_grid(data):
    """

    """
    grid2 = data.isel(time=0, height=0, drop=True).copy()

    vars1 = [v for v in list(grid2.variables) if (not v in ('lon', 'lat')) and (len(grid2[v].dims) == 2)]
    grid3 = grid2[vars1[0]].load().notnull()
    grid3.name = 'null_grid'

    return grid3


def cust_range(*args, rtol=1e-05, atol=1e-08, include=[True, True]):
    """
    Combines numpy.arange and numpy.isclose to mimic
    open, half-open and closed intervals.
    Avoids also floating point rounding errors as with
    >>> numpy.arange(1, 1.3, 0.1)
    array([1. , 1.1, 1.2, 1.3])

    args: [start, ]stop, [step, ]
        as in numpy.arange
    rtol, atol: floats
        floating point tolerance as in numpy.isclose
    include: boolean list-like, length 2
        if start and end point are included
    """
    # process arguments
    if len(args) == 1:
        start = 0
        stop = args[0]
        step = 1
    elif len(args) == 2:
        start, stop = args
        step = 1
    else:
        assert len(args) == 3
        start, stop, step = tuple(args)

    # determine number of segments
    n = (stop-start)/step + 1

    # do rounding for n
    if np.isclose(n, np.round(n), rtol=rtol, atol=atol):
        n = np.round(n)

    # correct for start/end is exluded
    if not include[0]:
        n -= 1
        start += step
    if not include[1]:
        n -= 1
        stop -= step

    return np.linspace(start, stop, int(n))


def chunk_data(data, block_length=None, time_interval=None, null_grid=None, split_heights_bands=True):
    """
    Function to split an n-dimensional dataset along the x and y dimensions. Optionally, add time and height dimensions if the array does not aready contain them.

    Parameters
    ----------
    data : DataSet
        An xarray DataSet processed with the proper Tethys dimensions (depending on the result_type).
    block_length : int, float
        The length in decimal degrees of the side of the square block to group the results.
    time_interval : int
        The interval or frequency that the time dimension should be chunked. The units are in days.
    null_grid : DataArray
        This only applies to grid data (with lat and lon). This is a boolean DataArray with dimensions lat and lon where True is where numeric data is contained.

    Returns
    -------
    List of Datasets
    """
    ## Get the dimension data
    dims = dict(data.dims)

    ## base chunk dict
    chunks_list = []

    ## Split geometry
    if isinstance(block_length, (float, int)):
        if block_length <= 0:
            if 'geometry' in dims:
                geo0 = [wkb.loads(s, hex=True) for s in data.geometry.values]

                if 'station_id' not in data:
                    geo1 = [assign_station_id(s) for s in geo0]
                    data = data.assign({'station_id': (('geometry'), geo1)})

                # Add in lats and lons for user convenience
                lats = [g.y for g in geo0]
                lons = [g.x for g in geo0]
                data = data.assign({'lon': (('geometry'), lons), 'lat': (('geometry'), lats)})

                chunks_list.append(data.copy())

            elif ('lat' in dims) and ('lon' in dims):
                for y in data.lat.values:
                    for x in data.lon.values:
                        if isinstance(null_grid, xr.DataArray):
                            ng1 = bool(null_grid.sel(lon=x, lat=y))
                            if ng1:
                                new1 = data.sel(lon=[x], lat=[y])

                                geo1 = Point(round(x, 7), round(y, 7))

                                new1 = new1.assign_coords(station_geometry=[geo1.wkb_hex])

                                geo1 = assign_station_id(geo1)
                                new1 = new1.assign({'station_id': (('station_geometry'), [geo1])})
                                chunks_list.append(new1.copy())
            else:
                raise ValueError('data has no geometry or lat/lon dimension(s).')
        else:
            if 'geometry' in dims:
                if dims['geometry'] > 1:
                    raise ValueError('If block_length is not None and geometry is part of the dims, then the total geometry count must be greater than one.')

                geo1 = data.geometry.values
                geo2 = {g: wkt.loads(wkt.dumps(wkb.loads(g, hex=True), rounding_precision=7)).centroid for g in geo1}
                geo3 = MultiPoint([g for i, g in geo2.items()])
                bounds = geo3.bounds

                lon_start = (((bounds[0] + 180)//block_length) * block_length) - 180
                x_range = np.arange(lon_start, bounds[2] + block_length, block_length)

                lat_start = (((bounds[1] + 45)//block_length) * block_length) - 45
                y_range = np.arange(lat_start, bounds[3] + block_length, block_length)

                geo_pos_dict = {}
                for iy, y in enumerate(y_range[1:]):
                    min_y = y_range[iy]
                    for ix, x in enumerate(x_range[1:]):
                        min_x = x_range[ix]
                        geos1 = [i for i, g in geo2.items() if (x > g.x >= min_x) and (y > g.y >= min_y)]
                        if geos1:
                            bounds_new = np.array([min_x, min_y, x, y]).round(7)
                            poly1 = box(*bounds_new)
                            poly1_hex = poly1.wkb_hex
                            geo_pos_dict[poly1_hex] = geos1

                for s, g in geo_pos_dict.items():
                    ## Using dropna here forces all of the data to be pulled into RAM
                    ## Should this be removed?
                    new1 = data.sel(geometry=g).dropna('time', how='all')

                    if 'station_id' in new1:
                        new1 = new1.drop_vars('station_id')
                    if 'station_geometry' in new1:
                        new1 = new1.drop_vars('station_geometry')

                    poly2 = wkb.loads(s, hex=True)
                    poly_stn_id = assign_station_id(poly2)

                    new1 = new1.assign_coords(station_geometry=[s])
                    new1 = new1.assign({'station_id': (('station_geometry'), [poly_stn_id])})
                    # Assign the lats and lons as variables against the geometry
                    geo0 = [wkb.loads(s, hex=True) for s in g]
                    lats = [g.y for g in geo0]
                    new1 = new1.assign({'lat': (('geometry'), lats)})
                    lons = [g.x for g in geo0]
                    new1 = new1.assign({'lon': (('geometry'), lons)})

                    # Append
                    chunks_list.append(new1.copy())


            elif ('lat' in dims) and ('lon' in dims):
                min_lat = float(data.lat.min())
                min_lon = float(data.lon.min())
                max_lat = float(data.lat.max())
                max_lon = float(data.lon.max())

                lon_start = (((min_lon + 180)//block_length) * block_length) - 180
                x_range = np.arange(lon_start, max_lon + block_length, block_length)
                lons = data.lon.values

                lat_start = (((min_lat + 45)//block_length) * block_length) - 45
                y_range = np.arange(lat_start, max_lat + block_length, block_length)
                lats = data.lat.values

                for iy, y in enumerate(y_range[1:]):
                    min_y = y_range[iy]
                    for ix, x in enumerate(x_range[1:]):
                        min_x = x_range[ix]

                        lon_slice = [(i <= x) & (i > min_x) for i in lons]
                        lat_slice = [(i <= y) & (i > min_y) for i in lats]

                        if isinstance(null_grid, xr.DataArray):
                            ng1 = null_grid.isel(lon=lon_slice, lat=lat_slice).copy()
                            # ng1 = null_grid.sel(lon=slice(min_x, x - 0.00001), lat=slice(min_y, y - 0.00001)).copy()
                            ng2 = xr.where(ng1, 1, np.nan)
                            ng3 = ng2.dropna('lon', how='all').dropna('lat', how='all')
                            geos1 = data.sel(lon=ng3.lon, lat=ng3.lat)
                        else:

                            geos1 = data.isel(lon=lon_slice, lat=lat_slice)
                            # geos1 = data.sel(lon=slice(min_x, x - 0.00001), lat=slice(min_y, y - 0.00001))

                        new_dims = geos1.dims

                        if (new_dims['lat'] > 0) and (new_dims['lon'] > 0):
                            bounds_new = np.array([min_x, min_y, x, y]).round(7)
                            poly1 = box(*bounds_new)
                            poly1_hex = poly1.wkb_hex
                            poly_stn_id = assign_station_id(poly1)

                            if 'station_id' in geos1:
                                geos1 = geos1.drop_vars('station_id')
                            if 'station_geometry' in geos1:
                                geos1 = geos1.drop_vars('station_geometry')

                            geos1 = geos1.assign_coords(station_geometry=[poly1_hex])
                            geos1 = geos1.assign({'station_id': (('station_geometry'), [poly_stn_id])})
                            chunks_list.append(geos1.copy())
            else:
                raise ValueError('data has no geometry or lat/lon dimension(s).')
    else:
        chunks_list.append(data.copy())


    ## Split times
    if isinstance(time_interval, int):
        base_days = 106751
        time_freq = '{}D'.format(time_interval)
        times1 = pd.to_datetime(data['time'].values)
        min_time = times1[0]
        min_days = min_time.timestamp()/60/60/24

        days_start = pd.Timestamp(int((((min_days + base_days)//time_interval) * time_interval) - base_days), unit='D')

        max_time = times1[-1]
        max_time2 = max_time + pd.DateOffset(days=time_interval)

        time_range = pd.date_range(days_start, max_time2, freq=time_freq)

        ## Time correction settings in case the time arrays got messed up in transit - with duplicated timestamps
        time_dup = times1.duplicated().any()
        if time_dup:
            print('Timestamps have duplicate values...attempting to correct...')

            data_freq = times1[:3].inferred_freq
            if not isinstance(data_freq, str):
                raise ValueError('The time frequency could not be determined, so no time correction will be applied.')
            else:
                ct = True

            time_range_corr = pd.date_range(min_time, max_time, freq=data_freq)

            if len(time_range_corr) != len(times1):
                raise ValueError('The new corrected times do not have the same length of the source data, so no time correction will be applied.')
            else:
                times1 = time_range_corr
        else:
            ct = False

        chunks = []

        for c in chunks_list:
            ## Correct for bad dates/data
            if ct:
                c['time'] = times1

            for i in time_range:
                new_times_bool = (times1 >= i) & (times1 < (i + pd.DateOffset(days=time_interval)))

                # c1 = c.sel(time=slice(i, i + pd.DateOffset(days=time_interval) - pd.DateOffset(seconds=1)))
                c1 = c.sel(time=new_times_bool)
                if c1.time.shape[0] > 0:
                    c1 = c1.assign_coords(chunk_date=[i])
                    if 'station_geometry' in c1:
                        c1 = c1.assign({'chunk_day': (('station_geometry', 'chunk_date'), [[np.int32(i.timestamp()/60/60/24)]])})
                    else:
                        c1 = c1.assign({'chunk_day': (('geometry', 'chunk_date'), [[np.int32(i.timestamp()/60/60/24)]])})
                    # c1.attrs['chunk_day'] = int(i.timestamp()/60/60/24)
                    chunks.append(c1.copy())

        chunks_list = chunks

        chunks = []
        del chunks

    ## Split heights
    if split_heights_bands:
        if 'height' in dims:
            if dims['height'] > 1:
                chunks = []

                for c in chunks_list:
                    for h in c.height.values:
                        chunks.append(c.sel(height=[h]).copy())

                chunks_list = chunks

                chunks = []
                del chunks

    ## Split bands
        if 'band' in dims:
            if dims['band'] > 1:
                chunks = []

                for c in chunks_list:
                    for b in c.band.values:
                        chunks.append(c.sel(band=[b]).copy())

                chunks_list = chunks

                chunks = []
                del chunks

    return chunks_list


def prepare_raster(image, parameter, x_name='x', y_name='y', band=1):
    """

    """
    xr1 = rxr.open_rasterio(image)
    xr1 = xr1.rename({x_name: 'lon', y_name: 'lat'}).sel(band=band).drop(['band', 'spatial_ref'])
    xr1.name = parameter

    attrs = xr1.attrs.copy()

    encoding = {'dtype': xr1.encoding['rasterio_dtype'], 'scale_factor': attrs['scale_factor'], 'add_offset': attrs['add_offset'], '_FillValue': -9999}

    xr1.encoding = encoding
    xr1.attrs = {}

    return xr1.to_dataset()


def save_dataset_stations(file_path, block_length, compression='zstd', remove_station_data=True):
    """

    """
    path1 = pathlib.Path(file_path)
    base_path = path1.parent

    if file_path.endswith('.nc'):
        ds_id = path1.stem

        data = xr.open_dataset(file_path)

        time1 = pd.Timestamp(data.time.values[0]).strftime('%Y%m%d%H%M%S')
        null_grid = calc_null_grid(data)
    elif file_path.endswith('.tif'):
        file_name = path1.stem
        ds_id, parameter, height1, time1 = file_name.split('--')

        time = pd.Timestamp(time1)
        height = float(height1)

        data = prepare_raster(file_path, parameter)
        null_grid = None

    chunks_list = chunk_data(data, block_length=block_length, time_interval=None, null_grid=null_grid, split_heights_bands=False)

    new_paths = []
    for c in chunks_list:
        stn_id = str(c['station_id'].values[0])
        file_name = ds_stn_file_str.format(ds_id=ds_id, stn_id=stn_id, date=time1)
        new_file_path = str(base_path.joinpath(file_name))

        if remove_station_data:
            b = c.drop_vars(['station_geometry', 'station_id'], errors='ignore').copy().load()
        else:
            b = c.copy().load()

        if file_path.endswith('.tif'):
            b = b.assign_coords(height=height).expand_dims('height', axis=2)
            b = b.assign_coords(time=time).expand_dims('time')

        if compression == 'zstd':
            new_file_path = new_file_path + '.zst'
            write_pkl_zstd(b.to_netcdf(), new_file_path)
        else:
            b.to_netcdf(new_file_path)

        b.close()
        c.close()
        del c
        del b

        new_paths.append(new_file_path)

    data.close()
    del data

    if null_grid is not None:
        null_grid.close()
        del null_grid

    os.remove(file_path)

    return new_paths


def reorder_parameter_dims(data):
    """

    """
    ## get parameters and determine the dims order
    result_type = data.attrs['result_type']
    model = tdm.dataset.result_type_dict[result_type]
    m1 = model(**dict(data.dims))
    m1_dict = m1.dict(exclude_none=True)
    dim_names_order = tuple(m1_dict.keys())
    parameter = [v for v in data.variables if 'dataset_id' in data[v].attrs][0]

    data_index, vars3, main_vars, ancillary_variables, vars_dict = extract_data_dimensions(data, parameter)

    if dim_names_order != data_index:
        data[parameter] = data[parameter].transpose(*dim_names_order)

        if ancillary_variables:
            for a in ancillary_variables:
                data[a] = data[a].transpose(*dim_names_order)

    return data


def hash_results(data, digest_size=12):
    """
    Hashing function for xarray data from Tethys. This hashes the primary results data (parameter) by first converting it to an int, then serializing it as json, then hashing with blake2. The data must either be either stored as int or float.

    Parameters
    ----------
    data : xr.Dataset
        A proper Tethys xarray Dataset object.
    digest_size : int
        The digest size for the blake2 hashing. Should be set to 12 for consistancy.

    Returns
    -------
    str
        hash
    """
    ## get parameters and determine the dims order
    result_type = data.attrs['result_type']
    model = tdm.dataset.result_type_dict[result_type]
    m1 = model(**dict(data.dims))
    m1_dict = m1.dict(exclude_none=True)
    dim_names_order = tuple(m1_dict.keys())
    # dim_values_order = tuple(m1_dict.values())
    parameter = [v for v in data.variables if 'dataset_id' in data[v].attrs][0]

    encoding = data[parameter].encoding.copy()

    results_dtype = data[parameter].dtype.name

    ## Convert the (likely) float to int. This creates a 1D array (regardless of the input dims).
    if 'float' in results_dtype:
        encoding1 = {}
        for k, v in encoding.items():
            if k == 'scale_factor':
                encoding1['scale'] = int(1/v)
            elif k == 'add_offset':
                encoding1['offset'] = v
            elif k == 'dtype':
                encoding1['astype'] = 'int'

        encoding1['dtype'] = data[parameter].dtype

        if 'offset' not in encoding1:
            encoding1['offset'] = 0
        if 'scale' not in encoding1:
            encoding1['scale'] = 1

        codec1 = numcodecs.FixedScaleOffset(**encoding1)
        values = codec1.encode(data[parameter].transpose(*dim_names_order).values)
    elif 'int' in results_dtype:
        values = data[parameter].transpose(*dim_names_order).values.flatten()
    else:
        raise TypeError('Input data must be either int or float.')

    ## Serialize to json bytes for hashing. For some reason, orjson cannot serialize int16 ndarrays...
    values_json = orjson.dumps(values, option=orjson.OPT_SERIALIZE_NUMPY)

    hash1 = blake2b(values_json, digest_size=digest_size).hexdigest()

    return hash1


def get_result_chunk_data(data):
    """

    """
    parameter = [v for v in data.variables if 'dataset_id' in data[v].attrs][0]
    dataset_id = data[parameter].attrs['dataset_id']

    version_date = pd.Timestamp(data.attrs['version_date']).tz_localize(None)
    system_version = int(data.attrs['system_version'])

    times = pd.to_datetime(data.time.values)
    from_date = times.min()
    to_date = times.max()

    hash1 = str(data['chunk_hash'].values.flatten()[0])
    chunk_id = str(data['chunk_id'].values.flatten()[0])
    stn_id = data['station_id'].values.flatten()[0]

    version_date_key = make_run_date_key(version_date)

    s3_key = tdm.utils.key_patterns[system_version]['results'].format(dataset_id=dataset_id, version_date=version_date_key, chunk_id=chunk_id, station_id=stn_id)

    dims = data.dims

    dict1 = {
             'version_date': version_date,
             'chunk_hash': hash1,
             'station_id': stn_id,
             'dataset_id': dataset_id,
             'chunk_id': chunk_id,
             'n_times': dims['time'],
             'from_date': from_date,
             'to_date': to_date,
             'key': s3_key
             }

    if 'height' in data:
        dict1['height'] = int(data['height'].values.flatten()[0] * 1000)
    if 'chunk_date' in data:
        dict1['chunk_day'] = int(data['chunk_day'].values.flatten()[0])
    if 'band' in data:
        dict1['band'] = int(data['band'].values.flatten()[0])

    return dict1


def add_extra_chunk_data(data):
    """

    """
    dims = list(data.dims)

    ## Hash data
    hash1 = hash_results(data)

    # This seems messy...
    if 'station_geometry' in dims:
        if 'band' in dims:
            coord = ('station_geometry', 'chunk_date', 'height', 'band')
        else:
            coord = ('station_geometry', 'chunk_date', 'height')
    elif 'geometry' in dims:
        if 'band' in dims:
            coord = ('geometry', 'chunk_date', 'height', 'band')
        else:
            coord = ('geometry', 'chunk_date', 'height')
    elif ('lon' in dims) and ('lat' in dims):
        if 'band' in dims:
            coord = ('lat', 'lon', 'chunk_date', 'height', 'band')
        else:
            coord = ('lat', 'lon', 'chunk_date', 'height')
    else:
        raise NotImplementedError('Need to add more permutations.')

    # if 'station_geometry' in dims:
    #     dims.remove('time')
    #     if 'geometry' in dims:
    #         dims.remove('geometry')

    hash2 = np.expand_dims(hash1, list(np.arange(len(coord))))
    data = data.assign({'chunk_hash': (coord, hash2)})

    ## Assign the chunk_id
    chunk_id_dict = {}

    if 'chunk_day' in data:
        chunk_id_dict['chunk_day'] = int(data['chunk_day'].values.flatten()[0])
    if 'height' in data:
        chunk_id_dict['height'] = int(data['height'].values[0]*1000)
    if 'band' in data:
        chunk_id_dict['band'] = int(data['band'].values[0])

    chunk_id = assign_chunk_id(chunk_id_dict)

    chunk_id2 = np.expand_dims(chunk_id, list(np.arange(len(coord))))

    data = data.assign({'chunk_id': (coord, chunk_id2)})

    return data


def save_new_results(nc_path, metadata, version_date, overwrite=False, system_version=4):
    """

    """
    chunk_params = metadata['chunk_parameters']
    block_length = chunk_params['block_length']
    time_interval = chunk_params['time_interval']
    result_type = metadata['result_type']

    path1 = pathlib.Path(nc_path)
    base_path = path1.parent

    if path1.suffix == '.zst':
        data = xr.load_dataset(utils.read_pkl_zstd(nc_path))
    elif path1.suffix == '.nc':
        data = xr.open_dataset(nc_path)
    else:
        raise TypeError('The nc_path must have an extension of zst or nc.')
    # _ = [data.attrs.pop(a) for a in ['CDO', 'CDI', 'history']]

    ds_id = metadata['dataset_id']

    if result_type == 'grid':
        null_grid = calc_null_grid(data)
    else:
        null_grid = None

    results_new_paths = []

    chunks_list = chunk_data(data, block_length=block_length, time_interval=time_interval, null_grid=null_grid, split_heights_bands=True)

    for b in chunks_list:
        f = b.copy().load()

        ## Update the metadata
        f = add_metadata_results(f, metadata, version_date)
        f = add_extra_chunk_data(f)

        ## Reoder dims if necessary
        f = reorder_parameter_dims(f)

        ## Get the variables for the output
        hash1 = str(f['chunk_hash'].values.flatten()[0])
        chunk_id = str(f['chunk_id'].values.flatten()[0])

        ## Save the object to a file
        stn_id = str(f['station_id'].values[0])
        version_date_key = make_run_date_key(version_date)
        file_name = results_file_str.format(ds_id=ds_id, stn_id=stn_id, chunk_id=chunk_id, hash=hash1, version_date=version_date_key)
        file_path = str(base_path.joinpath(file_name))

        if os.path.isfile(file_path) and (not overwrite):
            print(file_path + ' already exists!')
        else:
            write_pkl_zstd(f.to_netcdf(), file_path)
            results_new_paths.append(file_path)

        b.close()
        del b
        f.close()
        del f

    ## Remove old file
    if results_new_paths:
        if results_new_paths[0] != nc_path:
            os.remove(nc_path)
    else:
        os.remove(nc_path)

    return results_new_paths


def compute_scale_and_offset(min_value, max_value, n):
    """
    Computes the scale_factor and offset for the dataset using a min value and max value, and int n
    """
    # stretch/compress data to the available packed range
    scale_factor = (max_value - min_value) / (2 ** n - 1)

    # translate the range to be symmetric about zero
    add_offset = min_value + 2 ** (n - 1) * scale_factor

    return scale_factor, add_offset


def determine_duplicate_times(nc_paths, time_name, keep='first'):
    """

    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    nc_paths1.sort()

    ## Determine duplicate times
    if len(nc_paths1) > 1:
        xr1 = xr.open_mfdataset(nc_paths1[:2])

        time_bool = xr1.get_index(time_name).duplicated(keep=keep)

        xr1.close()
        del xr1

        time_len = int(len(time_bool)/2)
        time_index_bool = ~time_bool[time_len:]
    else:
        raise ValueError('nc_paths must have > 1 files.')

    return time_index_bool




