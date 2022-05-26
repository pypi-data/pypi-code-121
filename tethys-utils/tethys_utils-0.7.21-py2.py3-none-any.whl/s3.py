#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 13:30:43 2021

@author: mike
"""
import os
import numpy as np
import pandas as pd
import orjson
import tethys_data_models as tdm
from tethysts.utils import get_object_s3, read_json_zstd, s3_client, read_pkl_zstd
from tethys_utils.misc import make_run_date_key, path_date_parser, write_json_zstd
from tethysts import Tethys
from botocore import exceptions as bc_exceptions
from time import sleep
import pathlib
import concurrent.futures
import copy
import multiprocessing as mp
import botocore
from pydantic import HttpUrl
import zlib
# from hashlib import blake2b

############################################
### Parameters

results_file_str = '{ds_id}_{version_date}_{stn_id}_{chunk_id}_{hash}_results.nc.zst'

############################################
### Functions


def put_object_s3(s3, bucket, key, obj, metadata, content_type, retries=5):
    """

    """
    counter = retries
    while counter > 0:
        try:
            obj2 = s3.put_object(Bucket=bucket, Key=key, Body=obj, Metadata=metadata, ContentType=content_type)
            break
        except bc_exceptions.ConnectionClosedError as err:
            print(err)
            counter = counter - 1
            if counter == 0:
                raise err
            print('...trying again...')
            sleep(5)
        except bc_exceptions.ConnectTimeoutError as err:
            print(err)
            counter = counter - 1
            if counter == 0:
                raise err
            print('...trying again...')
            sleep(5)

    obj2.update({'key': key, 'bucket': bucket})

    return obj2


def put_file_s3(s3, bucket, key, file_path, metadata, content_type, retries=5):
    """

    """
    with open(file_path, 'rb') as f:
        obj_out = put_object_s3(s3, bucket, key, f.read(), metadata, content_type, retries=retries)

    return obj_out


def copy_object_s3(s3, source_bucket, dest_bucket, source_key, dest_key, retries=5):
    """
    Copies an object in an S3 database to another location in an S3 database. They must have the same fundemental connection_config. All metadata is copied to the new object.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object
    """
    source_dict = {'Bucket': source_bucket, 'Key': source_key}

    counter = retries
    while counter > 0:
        try:
            resp = s3.copy_object(Bucket=dest_bucket, Key=dest_key, CopySource=source_dict, MetadataDirective='COPY')
            break
        except bc_exceptions.ConnectionClosedError as err:
            print(err)
            counter = counter - 1
            if counter == 0:
                raise err
            print('...trying again...')
            sleep(5)
        except bc_exceptions.ConnectTimeoutError as err:
            print(err)
            counter = counter - 1
            if counter == 0:
                raise err
            print('...trying again...')
            sleep(5)

    return resp


def multi_copy_object_s3(s3, source_bucket, dest_bucket, source_dest_keys, retries=5, threads=30):
    """
    Same as the copy_object_s3 except with multi threading. The input source_dest_keys must be a list of dictionaries with keys named source_key and dest_key.
    """
    keys = copy.deepcopy(source_dest_keys)

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for key in keys:
            key['s3'] = s3
            key['source_bucket'] = source_bucket
            key['dest_bucket'] = dest_bucket
            f = executor.submit(copy_object_s3, **key)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    resp_list = [r.result() for r in runs[0]]

    return resp_list


def put_interim_results_s3(s3, bucket, file_path, run_id, system_version=4, retries=5):
    """

    """
    path1 = pathlib.Path(file_path)
    ds_id, stn_id, start_date = path1.stem.split('.')[0].split('_')
    key = tdm.utils.key_patterns[system_version]['interim_results'].format(run_id=run_id, dataset_id=ds_id, station_id=stn_id, start_date=start_date)

    stats = os.stat(file_path)
    run_date = pd.Timestamp(round(stats.st_mtime), unit='s')
    run_date_key = make_run_date_key(run_date)

    _ = put_file_s3(s3, bucket, key, file_path, {'run_date': run_date_key}, 'application/zstd', retries=retries)

    return key


def list_objects_s3(s3, bucket, prefix, start_after='', delimiter='', continuation_token='', date_format=None):
    """
    Wrapper S3 function around the list_objects_v2 base function with a Pandas DataFrame output.

    Parameters
    ----------
    s3_client : boto3.client
        A boto3 client object
    bucket : str
        The S3 bucket.
    prefix : str
        Limits the response to keys that begin with the specified prefix.
    start_after : str
        The S3 key to start after.
    delimiter : str
        A delimiter is a character you use to group keys.
    continuation_token : str
        ContinuationToken indicates to S3 that the list is being continued on this bucket with a token.

    Returns
    -------
    DataFrame
    """
    if s3._endpoint.host == 'https://vault.revera.co.nz':
        js = []
        while True:
            js1 = s3.list_objects(Bucket=bucket, Prefix=prefix, Marker=start_after, Delimiter=delimiter)

            if 'Contents' in js1:
                js.extend(js1['Contents'])
                if 'NextMarker' in js1:
                    start_after = js1['NextMarker']
                else:
                    break
            else:
                break

    else:
        js = []
        while True:
            js1 = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, StartAfter=start_after, Delimiter=delimiter, ContinuationToken=continuation_token)

            if 'Contents' in js1:
                js.extend(js1['Contents'])
                if 'NextContinuationToken' in js1:
                    continuation_token = js1['NextContinuationToken']
                else:
                    break
            else:
                break

    if js:
        f_df1 = pd.DataFrame(js)[['Key', 'LastModified', 'ETag', 'Size']].copy()
        if isinstance(date_format, str):
            f_df1['KeyDate'] = pd.to_datetime(f_df1.Key.apply(lambda x: path_date_parser(x, date_format)), utc=True, errors='coerce').dt.tz_localize(None)
        f_df1['ETag'] = f_df1['ETag'].str.replace('"', '')
        f_df1['LastModified'] = pd.to_datetime(f_df1['LastModified']).dt.tz_localize(None)
    else:
        if isinstance(date_format, str):
            f_df1 = pd.DataFrame(columns=['Key', 'LastModified', 'ETag', 'Size', 'KeyDate'])
        else:
            f_df1 = pd.DataFrame(columns=['Key', 'LastModified', 'ETag', 'Size'])

    return f_df1


def list_object_versions_s3(s3_client, bucket, prefix, start_after='', delimiter=None, date_format=None):
    """
    Wrapper S3 function around the list_object_versions base function with a Pandas DataFrame output.

    Parameters
    ----------
    s3_client : boto3.client
        A boto3 client object
    bucket : str
        The S3 bucket.
    prefix : str
        Limits the response to keys that begin with the specified prefix.
    start_after : str
        The S3 key to start at.
    delimiter : str or None
        A delimiter is a character you use to group keys.

    Returns
    -------
    DataFrame
    """
    js = []
    while True:
        if isinstance(delimiter, str):
            js1 = s3_client.list_object_versions(Bucket=bucket, Prefix=prefix, KeyMarker=start_after, Delimiter=delimiter)
        else:
            js1 = s3_client.list_object_versions(Bucket=bucket, Prefix=prefix, KeyMarker=start_after)

        if 'Versions' in js1:
            js.extend(js1['Versions'])
            if 'NextKeyMarker' in js1:
                start_after = js1['NextKeyMarker']
            else:
                break
        else:
            break

    if js:
        f_df1 = pd.DataFrame(js)[['Key', 'VersionId', 'IsLatest', 'LastModified', 'ETag', 'Size']].copy()
        if isinstance(date_format, str):
            f_df1['KeyDate'] = pd.to_datetime(f_df1.Key.apply(lambda x: path_date_parser(x, date_format)), utc=True, errors='coerce').dt.tz_localize(None)
        f_df1['ETag'] = f_df1['ETag'].str.replace('"', '')
        f_df1['LastModified'] = pd.to_datetime(f_df1['LastModified']).dt.tz_localize(None)
    else:
        if isinstance(date_format, str):
            f_df1 = pd.DataFrame(columns=['Key', 'VersionId', 'IsLatest', 'LastModified', 'ETag', 'Size', 'KeyDate'])
        else:
            f_df1 = pd.DataFrame(columns=['Key', 'VersionId', 'IsLatest', 'LastModified', 'ETag', 'Size'])

    return f_df1


def get_remote_stations(bucket, dataset_id, version_date, s3=None, connection_config=None, public_url=None, system_version=4):
    """

    """
    vd = make_run_date_key(version_date)
    key = tdm.utils.key_patterns[system_version]['stations'].format(dataset_id=dataset_id, version_date=vd)

    try:
        obj1 = get_object_s3(key, bucket, s3, connection_config, public_url)
        rem_stn = read_json_zstd(obj1)
    except:
        rem_stn = None

    return rem_stn


def get_remote_results_chunks(bucket, dataset_id, version_date, s3=None, connection_config=None, public_url=None, system_version=4):
    """

    """
    vd = make_run_date_key(version_date)
    key = tdm.utils.key_patterns[system_version]['results_chunks'].format(dataset_id=dataset_id, version_date=vd)

    try:
        obj1 = get_object_s3(key, bucket, s3, connection_config, public_url)
        rem_ds = read_json_zstd(obj1)
    except:
        rem_ds = None

    return rem_ds


def delete_dataset_s3(conn_config, bucket, dataset_id, system_version=4):
    """
    Function to delete Tethys result objects including all object versions.

    Parameters
    ----------
    conn_config : dict
        A dictionary of the connection info necessary to establish an S3 connection.
    bucket : str
        The s3 bucket.
    dataset_id : str
        The specific dataset that should be removed.

    Returns
    -------
    list of keys deleted
    """
    s3 = s3_client(conn_config)

    ## Update/Remove the dataset from the master datasets file
    dss_key = tdm.utils.key_patterns[system_version]['datasets']

    dss_obj = get_object_s3(dss_key, bucket, s3)

    rem_keys = []

    if dss_obj is not None:
        dss_list = read_json_zstd(dss_obj)

        dss_list_new = []
        for dss in dss_list:
            if dss['dataset_id'] != dataset_id:
                dss_list_new.append(dss)

        if len(dss_list_new) > 0:
            content_type = 'application/json'

            run_date_key = make_run_date_key()
            metadata = {'run_date': run_date_key}

            dss_obj_new = write_json_zstd(dss_list_new)

            resp = put_object_s3(s3, bucket, dss_key, dss_obj_new, metadata, content_type)
        else:
            obj_list = list_object_versions_s3(s3, bucket, dss_key)
            obj_del = obj_list[['Key', 'VersionId']].to_dict('records')
            resp = s3.delete_objects(Bucket=bucket, Delete={'Objects': obj_del, 'Quiet': True})
            rem_keys.extend(obj_del)

        ## Remove all of the other objects
        del_results = tdm.utils.key_patterns[system_version]['results'].split('{version_date}')[0].format(dataset_id=dataset_id)
        del_versions = tdm.utils.key_patterns[system_version]['versions'].format(dataset_id=dataset_id)
        del_dataset = tdm.utils.key_patterns[system_version]['dataset'].format(dataset_id=dataset_id)
        # del_stations = tdm.utils.key_patterns[system_version]['stations'].format(dataset_id=dataset_id)

        del_list = [del_dataset, del_versions, del_results]

        for prefix in del_list:

            obj_list = list_object_versions_s3(s3, bucket, prefix)

            if not obj_list.empty:
                obj_del = obj_list[['Key', 'VersionId']].to_dict('records')

                ## Split them into 1000 key chunks
                rem_keys_chunks = np.array_split(obj_del, int(np.ceil(len(obj_del)/1000)))

                ## Run through and delete the objects...
                for keys in rem_keys_chunks:
                    resp = s3.delete_objects(Bucket=bucket, Delete={'Objects': keys.tolist(), 'Quiet': True})

                rem_keys.extend(obj_del)
    else:
        print('No dataset found with the given dataset_id.')

    return rem_keys


def get_versions(dataset_ids, bucket, s3=None, connection_config=None, public_url=None, system_version=4):
    """

    """
    remote1 = dict(s3=s3, connection_config=connection_config, public_url=public_url, bucket=bucket, version=system_version)
    remote2 = copy.deepcopy(remote1)
    _ = remote2.pop('version')
    remote2['counter'] = 2

    t1 = Tethys([remote1])
    datasets = t1._datasets
    ds_ids = list(datasets.keys())

    rv_dict = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for ds_id in dataset_ids:
            if ds_id in ds_ids:
                rv_key = tdm.key_patterns[system_version]['versions'].format(dataset_id=ds_id)
                remote2['obj_key'] = rv_key
                f = executor.submit(get_object_s3, **remote2)
                futures.append(f)
                rv_dict[ds_id] = []
        runs = concurrent.futures.wait(futures)

    rv_list = [read_json_zstd(r.result()) for r in runs[0]]

    for rv in rv_list:
        ds_id = rv[0]['dataset_id']
        rv_dict[ds_id] = rv

    return rv_dict


def process_dataset_versions(dataset_list, bucket, version_data, s3=None, connection_config=None, public_url=None, system_version=4):
    """
    Function to process the run date keys for all datasets for the extraction.

    Parameters
    ----------
    dataset_list : list of dict
        The list of datasets, which is the output of the process_datasets function.
    remote : dict
        Dict of a connection_config and bucket:
        conn_config : dict
            A dictionary of the connection info necessary to establish an S3 connection.
        bucket : str
            The S3 bucket.

    Returns
    -------
    run_date_dict : dict of str
    """
    remote1 = dict(s3=s3, connection_config=connection_config, public_url=public_url, bucket=bucket, version=system_version)

    ## Build the ResultVersion model
    mod_date = pd.Timestamp.today(tz='utc').tz_localize(None).round('s')

    if isinstance(version_data['version_date'], str):
        version_data['version_date'] = pd.Timestamp(version_data['version_date'])

    version_data['modified_date'] = mod_date

    version_dict = {}
    for ds in dataset_list:
        dataset_id = ds['dataset_id']
        vd = version_data.copy()
        vd['dataset_id'] = dataset_id
        version_m = tdm.dataset.ResultVersion(**vd)
        version_dict[dataset_id] = orjson.loads(version_m.json(exclude_none=True))

    ## Check to make sure that the passed version date is not earlier than existing versions
    old_versions = get_versions(list(version_dict.keys()), bucket, s3, connection_config, public_url, system_version)

    for ds_id, vd in version_dict.items():
        if ds_id in old_versions.keys():
            new_date = pd.Timestamp(vd['version_date'])
            vd_old = old_versions[ds_id]
            old_date = pd.to_datetime([pd.Timestamp(v['version_date']) for v in vd_old]).max()
            if new_date < old_date:
                raise ValueError('The new version date is prior to the max old version date. New version date: {new_date}; old max version date: {old_date}. dataset_id: {ds_id}.'.format(new_date=new_date.isoformat(), old_date=old_date.isoformat(), ds_id=ds_id))

    return version_dict


def dataset_results_chunks_diff(ds_id, chunks_df, remote, add_old=False):
    """

    """
    tethys = Tethys([remote])
    datasets = tethys._datasets

    if ds_id in datasets:
        # dataset = datasets[ds_id]
        # method = dataset['method']
        vd_old = tethys.get_versions(ds_id)
        vd_max = chunks_df.version_date.max()

        # Check to make sure new version data is greater or equal to old dates
        vd0 = [vd['version_date'] for vd in vd_old if pd.Timestamp(vd['version_date']) <= vd_max]

        if not vd0:
            raise ValueError('The new version date must be greater than or equal to the old version dates.')

        # Determine what version date to use
        vd1 = [vd['version_date'] for vd in vd_old if pd.Timestamp(vd['version_date']) == vd_max]

        if len(vd1) > 0:
            vd = vd1[-1]
            merge_vals = ['conflict', 'new']
        else:
            if add_old:
                vd = vd_old[-1]['version_date']
                merge_vals = ['conflict', 'new', 'old']
            else:
                chunks_df['key'] = np.nan
                chunks_df['_merge'] = 'new'

                return chunks_df

        # Load in the results chunks
        vd_key = make_run_date_key(vd)
        rc_key = tdm.utils.key_patterns[4]['results_chunks'].format(dataset_id=ds_id, version_date=vd_key)

        s_remote = copy.deepcopy(remote)
        _ = s_remote.pop('version')
        s_remote['obj_key'] = rc_key

        rc_obj = get_object_s3(**s_remote)
        chunks1 = read_json_zstd(rc_obj)

        new_chunks_df = pd.DataFrame(chunks1).drop(['version_date', 'content_length', 'height', 'chunk_day'], axis=1).rename(columns={'chunk_hash': 'original_chunk_hash'})

        # Combine to determine which chunks should be assessed
        combo1 = pd.merge(chunks_df, new_chunks_df, on=['dataset_id', 'station_id', 'chunk_id'], indicator=True, how='outer')
        combo1 = combo1.replace({'_merge': {'both': 'conflict', 'left_only': 'new', 'right_only': 'old'}})
        combo1 = combo1[combo1['_merge'].isin(merge_vals)].copy()
        combo1['version_date'] = vd_max

        combo1['_merge'] = combo1['_merge'].astype("category").cat.set_categories(['identical', 'conflict', 'new', 'old'])
        combo1.loc[combo1['chunk_hash'] == combo1['original_chunk_hash'], '_merge'] = 'identical'

        chunks_df = combo1.drop(['original_chunk_hash'], axis=1)
    else:
        chunks_df['key'] = np.nan
        chunks_df['_merge'] = 'new'

    return chunks_df


def determine_results_chunks_diffs(source_paths, remote, add_old=False, max_workers=4):
    """

    """
    paths1 = []
    for p in source_paths:
        ds_id, version_date1, stn_id, chunk_id, hash_id, _ = os.path.split(p)[1].split('_')
        paths1.append([p, ds_id, version_date1, stn_id, chunk_id, hash_id])

    paths2 = pd.DataFrame(paths1, columns=['file_path', 'dataset_id', 'version_date', 'station_id', 'chunk_id', 'chunk_hash'])
    paths2['version_date'] = pd.to_datetime(paths2['version_date']).dt.tz_localize(None)

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for ds_id, chunks_df in paths2.groupby('dataset_id'):
            f = executor.submit(dataset_results_chunks_diff, ds_id, chunks_df, remote, add_old)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    updated_dfs = [r.result() for r in runs[0]]

    combo2 = pd.concat(updated_dfs)

    return combo2


def download_results(key, path, bucket: str, s3: botocore.client.BaseClient = None, connection_config: dict = None, public_url: HttpUrl=None):
    """

    """
    _, _, ds_id, version_date_key, stn_id, chunk_id1 = key.split('/')
    chunk_id = chunk_id1.split('.')[0]

    file_name = results_file_str.format(ds_id=ds_id, stn_id=stn_id, chunk_id=chunk_id, hash='none', version_date=version_date_key)
    out_path = os.path.join(path, file_name)

    counter = 3
    while True:
        obj1 = get_object_s3(key, bucket, s3, connection_config, public_url)

        source_checksum = zlib.adler32(obj1)

        try:
            # source_checksum = blake2b(obj1, digest_size=12).hexdigest()

            # try:
            #     _ = read_pkl_zstd(obj1)
            #     break
            # except:
            #     if counter == 0:
            #         raise ValueError('{} has corrupted data.'.format(key))
            #     else:
            #         counter = counter - 1
            #         print('Object was corrupted in transit...trying again...')
            #         sleep(5)

            with open(out_path, 'wb') as f:
                f.write(obj1)

            ## Test the write
            with open(out_path, 'rb') as f:
                file_checksum = zlib.adler32(f.read())

            if source_checksum == file_checksum:
                break
            else:
                raise ValueError('checksum mismatch...')
        except Exception as err:
            print(str(err))
            sleep(2)
            counter = counter - 1
            if counter <= 0:
                raise err

    del obj1

    return out_path




























































