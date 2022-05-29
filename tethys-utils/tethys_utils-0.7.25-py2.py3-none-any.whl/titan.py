#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 13:39:58 2021

@author: mike
"""
import os
import numpy as np
import xarray as xr
import pandas as pd
from tethys_utils import misc, s3, processing
from tethysts.utils import s3_client, get_object_s3, read_json_zstd, read_pkl_zstd, download_results, create_public_s3_url, make_run_date_key
import tethys_data_models as tdm
from typing import List, Optional, Dict, Union
from botocore import exceptions as bc_exceptions
import requests
import uuid
from cryptography.fernet import Fernet
import pandas as pd
from pydantic import HttpUrl
import concurrent.futures
import copy
import pathlib
import glob
import multiprocessing as mp
import random
from time import sleep
import shutil

##############################################
### Parameters

b2_dl_by_id = 'https://b2.tethys-ts.xyz/b2api/v1/b2_download_file_by_id?fileId={obj_id}'

preprocessed_dir = 'preprocessed_data'
previous_dir = 'previous_data'
# final_dir = 'final_results'

###############################################
### Helper functions



# def save_chunks(chunks_list, output_path):
#     """

#     """
#     for c in chunks_list:
#         chunk_json = tdm.dataset.ChunkID(height=int(c.height.values[0] * 1000), start_date=int(c.attrs['start_date'])).json(exclude_none=True).encode('utf-8')
#         chunk_id = blake2b(chunk_json, digest_size=12).hexdigest()
#         stn_id = str(c.station_id.values[0])
#         file_path = os.path.join(output_path, stn_id + '_' + chunk_id + '.nc.zst')

#         b = c.copy().load()

#         obj1 = misc.write_pkl_zstd(b.to_netcdf(), file_path)

#         b.close()
#         del b
#         del obj1


###############################################
### Class


class Titan(object):
    """

    """

    def __init__(self, temp_path: pathlib.Path, add_old: bool, run_id: str = None, key: str = None, diagnostics_url: HttpUrl = None):
        """
        The base class that does all the preparation of the datasets and saving to the S3 remote.

        Parameters
        ----------
        temp_path: str path or pathlib.Path
            The path to the temporary processing directory. Must be writable.
        add_old: bool
            Should previous version's results be added to new versions? Generally, this should be True for time_series sensor_recordings and False for simulation data.
        run_id: str
            The unique run_id given the last time Titan was initialised for the same processing task. This is only necessary when you want to continue an processing task.
        key: str
            The encryption key to the diagnostics file created from an earlier run. Similar to run_id; it is only necessary when you want to continue an processing task and you have saved the diagnostics file to the remote.
        diagnostics_url: http url str
            The http url to the diagnostics file. The key must also be provided.

        Returns
        -------
        Titan object
        """
        ## Check temp path
        os.makedirs(temp_path, exist_ok=True)

        if not os.access(temp_path, os.W_OK):
            raise OSError('{} has no write access.'.format(temp_path))

        ## Add in the additional paths
        preprocessed_path = os.path.join(temp_path, preprocessed_dir)
        previous_path = os.path.join(temp_path, previous_dir)
        # final_path = os.path.join(temp_path, final_dir)
        os.makedirs(preprocessed_path, exist_ok=True)
        os.makedirs(previous_path, exist_ok=True)
        # os.makedirs(final_path, exist_ok=True)

        self.preprocessed_path = preprocessed_path
        self.previous_path = previous_path
        # self.final_path = final_path

        self._add_old = add_old

        ## Test for the run_id and key
        need_dgn = True

        if isinstance(key, str) and (diagnostics_url is not None):
            # Attempt to read the diagnostics file
            try:
                resp = requests.get(diagnostics_url)
                f = Fernet(key)
                dgn = read_json_zstd(f.decrypt(resp.content))
                run_id = dgn['run_id']
                need_dgn = False

                _ = [setattr(self, k, v) for k, v in dgn['attributes'].items()]
                print('Diagnostics file has loaded sucessfully.')
            except:
                print('Reading diagnostics file failed. Check the URL link. If you continue, the diagnostics file will be overwritten.')

        if (not isinstance(key, str)):
            key = Fernet.generate_key().decode()
            print('A new encryption key has been generated. Keep it safe and secret:')
            print(key)

        if isinstance(run_id, str):
            if len(run_id) != 14:
                print('The run_id provided is not correct, setting a new one.')
                run_id = uuid.uuid4().hex[:14]
                print('A new run_id has been generated:')
                print(run_id)
        else:
            run_id = uuid.uuid4().hex[:14]
            print('A new run_id has been generated:')
            print(run_id)

        self.key = key
        self.run_id = run_id
        self.temp_path = temp_path
        self._results_objects_updated = []

        ## Set up diagnostics dict
        if need_dgn:
            run_date1 = misc.make_run_date_key()
            dgn = {'attributes': {},
                   'run_id': run_id,
                   'run_date': run_date1,
                   'key': key
                   }

        self.diagnostics = dgn

        pass


    @staticmethod
    def combine_dataset_metadata(project, datasets):
        """
        Combines project metadata with many datasets.

        Parameters
        ----------
        project: dict
        datasets: list of dict

        Returns
        -------
        list of dict with project added
        """
        datasets1 = []
        for d in datasets:
            d1 = copy.deepcopy(d)
            d1.update(project)
            datasets1.append(d1)

        return datasets1


    def status_checks(self, connection_config: tdm.base.ConnectionConfig, bucket: str, public_url: str = None, system_version: int = 4, load_diagnostics: bool = False):
        """

        """
        ## Test S3 connection
        _ = tdm.base.Remote(**{'connection_config': connection_config, 'bucket': bucket, 'version': system_version})
        client = s3_client(connection_config)

        # Read permissions
        try:
            _ = client.head_bucket(Bucket=bucket)
        except Exception as err:
            response_code = err.response['Error']['Code']
            if response_code == '403':
                raise requests.exceptions.ConnectionError('403 error. The connection_config is probably wrong.')
            elif response_code == '404':
                raise requests.exceptions.ConnectionError('404 error. The bucket was not found.')

        # Write permissions
        test1 = b'write test'
        test_key = 'tethys/testing/test_write.txt'

        try:
            _ = s3.put_object_s3(client, bucket, test_key, test1, {}, '', retries=1)
        except bc_exceptions.ConnectionClosedError:
            raise ValueError('Account does not have write permissions.')

        # Public URL read test
        if isinstance(public_url, str):
            try:
                _ = tdm.base.Remote(**{'public_url': public_url, 'bucket': bucket, 'version': system_version})
                _ = get_object_s3(test_key, public_url=public_url, bucket=bucket, counter=1)
            except:
                raise ValueError('public_url does not work.')

        ## Check that the S3 version is valid
        if not system_version in tdm.key_patterns:
            raise ValueError('S3 version must be one of {}.'.format(list(tdm.key_patterns.keys())))

        ## Check if there is an existing Tethys S3 version
        # Version 3+ check
        objs1 = s3.list_objects_s3(client, bucket, 'tethys/', delimiter='/')
        if not objs1.empty:
            exist_version = int(objs1.iloc[0].Key.split('/')[1].split('.')[0][1:])
        else:
        # Version 2 check
            objs2 = s3.list_objects_s3(client, bucket, 'tethys/v2/', delimiter='/')
            if objs2.empty:
                exist_version = None
            else:
                exist_version = 2

        if isinstance(exist_version, int):
            if exist_version != system_version:
                print('The bucket already has Tethys data and is version {}. You have been warned...'.format(exist_version))

        print('All status checks passed!')

        ## Save parameters
        setattr(self, 'connection_config', connection_config)
        setattr(self, 'bucket', bucket)
        setattr(self, 'public_url', public_url)
        setattr(self, 'system_version', system_version)

        ## Loading diagnostic log if it exists
        if load_diagnostics:
            dgn_key_pattern = tdm.key_patterns[self.system_version]['diagnostics']
            dgn_key = dgn_key_pattern.format(run_id=self.run_id)

            try:
                resp = get_object_s3(dgn_key, bucket, client, public_url=public_url, counter=0)
                f = Fernet(self.key)
                dgn = read_json_zstd(f.decrypt(resp))
                self.diagnostics = dgn
                _ = [setattr(self, k, v) for k, v in dgn['attributes'].items()]
                print('Diagnostics log found and loaded.')
            except:
                ## diagnostic log
                self.diagnostics['status_checks'] = {'pass': True}
                self.diagnostics['attributes'].update({'connection_config': connection_config, 'bucket': bucket, 'public_url': public_url, 'system_version': system_version})
        else:
            ## diagnostic log
            self.diagnostics['status_checks'] = {'pass': True}
            self.diagnostics['attributes'].update({'connection_config': connection_config, 'bucket': bucket, 'public_url': public_url, 'system_version': system_version})


    def save_diagnostics(self):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'status_checks')

        f = Fernet(self.key)
        dgn_obj = f.encrypt(misc.write_json_zstd(copy.deepcopy(self.diagnostics)))

        dgn_key_pattern = tdm.key_patterns[self.system_version]['diagnostics']
        dgn_key = dgn_key_pattern.format(run_id=self.run_id)

        client = s3_client(self.connection_config)
        run_date1 = misc.make_run_date_key()

        obj_resp = s3.put_object_s3(client, self.bucket, dgn_key, dgn_obj, {'run_date': run_date1}, 'application/json')

        self.diagnostics['diagnostic_s3_obj_id'] = obj_resp['VersionId']

        if isinstance(self.public_url, str):
            dgn_url = create_public_s3_url(self.public_url, self.bucket, dgn_key)
        else:
            dgn_url = ''

        return dgn_url


    def load_dataset_metadata(self, datasets: Union[dict, list]):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'status_checks')

        dataset_list = processing.process_datasets(datasets)

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

        ## Might keep this for later...
        # chunk_params_bool_list = []
        # for ds in dataset_list:
        #     if 'chunk_parameters' in ds:
        #         _ = tdm.dataset.ChunkParams(**ds['chunk_parameters'])
        #         chunk_params_bool_list.extend([True])
        #     else:
        #         chunk_params_bool_list.extend([True])

        # if all(chunk_params_bool_list):
        #     self.diagnostics['set_chunking_parameters'] = {'pass': True}

        ## Validate dataset model
        for ds in dataset_list:
            _ = tdm.dataset.Dataset(**ds)

        ## Set attributes
        ds_dict = {ds['dataset_id']: ds for ds in dataset_list}

        setattr(self, 'dataset_list', dataset_list)
        setattr(self, 'datasets', ds_dict)

        ## diagnostic log
        self.diagnostics['load_dataset_metadata'] = {'pass': True}
        self.diagnostics['attributes'].update({'dataset_list': dataset_list, 'datasets': ds_dict})


    # def set_chunking_parameters(self, block_length, time_interval=None):
    #     """

    #     """
    #     misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

    #     chunk_params = tdm.dataset.ChunkParams(block_length=block_length, time_interval=time_interval).dict(exclude_none=True)

    #     datasets = []
    #     for ds in self.dataset_list:
    #         ds['chunk_parameters'] = chunk_params
    #         datasets.append(ds)

    #     self.load_dataset_metadata(datasets)


    def process_versions(self, version_data: dict):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

        version_dict = s3.process_dataset_versions(self.dataset_list, bucket=self.bucket, connection_config=self.connection_config, public_url=self.public_url, version_data=version_data, system_version=self.system_version)
        max_version_date = max(list([d['version_date'] for d in version_dict.values()]))

        # setattr(self, 'processing_code', processing_code)
        setattr(self, 'version_dict', version_dict)
        setattr(self, 'max_version_date', max_version_date)

        ## diagnostic log
        self.diagnostics['process_versions'] = {'pass': True}
        self.diagnostics['attributes'].update({'version_dict': version_dict, 'max_version_date': max_version_date})

        return version_dict


    def _save_new_results(self, source_paths, max_workers=4):
        """

        """
        # misc.diagnostic_check(self.diagnostics, 'merge_nc_files')
        misc.diagnostic_check(self.diagnostics, 'process_versions')

        ## Put the big files first
        merge_list = [[p, os.path.getsize(p)] for p in list(set(source_paths))]
        merge_df = pd.DataFrame(merge_list, columns=['path', 'size'])

        source_paths1 = merge_df.sort_values('size', ascending=False).path.tolist()

        ## Iterate through files
        if max_workers <= 1:
            results_new_paths1 = []
            for source_path in source_paths1:
                ds_id = source_path.split('/')[-1].split('_')[0]
                metadata = self.datasets[ds_id]
                f = processing.save_new_results(source_path, metadata, self.max_version_date, self.system_version)
                results_new_paths1.extend(f)
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
                futures = []
                for source_path in source_paths1:
                    ds_id = source_path.split('/')[-1].split('_')[0]
                    metadata = self.datasets[ds_id]
                    f = executor.submit(processing.save_new_results, source_path, metadata, self.max_version_date, self.system_version)
                    futures.append(f)
                runs = concurrent.futures.wait(futures)

            ## process output
            results_new_paths1 = []
            extend = results_new_paths1.extend
            _ = [extend(r.result()) for r in runs[0]]

        results_new_paths1.sort()

        ## diagnostic log
        self.diagnostics['save_new_results'] = {'pass': True}

        return results_new_paths1


    def _determine_results_chunks_diffs(self, source_paths, remote, add_old=False, max_workers=4):
        """

        """
        r_chunks = s3.determine_results_chunks_diffs(source_paths, remote, add_old, max_workers)

        self._results_chunks_diffs = r_chunks

        return r_chunks


    def _update_conflicting_results(self, results_paths, rc_diffs, threads=60, max_workers=4):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'save_new_results')

        ## Determine the chunks that have conflicts
        r_chunks1 = rc_diffs[rc_diffs['_merge'] == 'conflict'].copy()

        if not r_chunks1.empty:
            chunks = r_chunks1.to_dict('records')

            ## Download old chunks for comparisons
            if isinstance(self.public_url, str):
                remote1 = {'bucket': self.bucket, 'public_url': self.public_url}
            else:
                remote1 = {'bucket': self.bucket, 'connection_config': self.connection_config}

            remote2 = copy.deepcopy(remote1)
            remote2['cache'] = pathlib.Path(self.previous_path)

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for chunk in chunks:
                    remote2['chunk'] = chunk
                    f = executor.submit(download_results, **remote2)
                    futures.append(f)
                runs = concurrent.futures.wait(futures)

            chunks1 = [r.result()['chunk'] for r in runs[0]]

            ## Update the results files
            if max_workers <= 1:
                updated_paths = []
                for chunk in chunks1:
                    ds_id = str(chunk).split('/')[-3]
                    metadata = self.datasets[ds_id]
                    p1 = processing.update_compare_results(chunk, metadata, self.max_version_date, self.preprocessed_path)
                    updated_paths.append(p1)
            else:
                with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
                    futures = []
                    for chunk in chunks1:
                        ds_id = str(chunk).split('/')[-3]
                        metadata = self.datasets[ds_id]
                        f = executor.submit(processing.update_compare_results, chunk, metadata, self.max_version_date, self.preprocessed_path)
                        futures.append(f)
                    runs = concurrent.futures.wait(futures)

                updated_paths = [r.result() for r in runs[0]]

            ## Remove previous results
            for chunk in chunks1:
                if chunk.exists():
                    os.remove(chunk)

        else:
            updated_paths = []

        ## Combine updated paths with "new" paths
        new_data_paths = rc_diffs[rc_diffs['_merge'] == 'new']['file_path'].tolist()
        updated_paths.extend(new_data_paths)
        updated_paths.sort()

        ## Remove files labeled as "identical"
        ident1 = rc_diffs[rc_diffs['_merge'] == 'identical']

        if not ident1.empty:
            paths = ident1['file_path'].tolist()
            for path in paths:
                if os.path.exists(path):
                    os.remove(path)

        ## diagnostic log
        self.diagnostics['update_conflicting_results'] = {'pass': True}

        return updated_paths


    def _update_results_chunks(self, results_paths, rc_diffs, old_versions, max_workers=4):
        """

        """
        ## checks
        misc.diagnostic_check(self.diagnostics, 'save_new_results')

        add_old = self._add_old
        if self._add_old:
            misc.diagnostic_check(self.diagnostics, 'update_conflicting_results')

        if rc_diffs is not None:
            r_chunks1 = rc_diffs[rc_diffs['_merge'] == 'conflict']

            if not r_chunks1.empty:
                misc.diagnostic_check(self.diagnostics, 'update_conflicting_results')

        ## Organise the paths
        paths_dict = {}
        for path in list(set(results_paths)):
            path1 = os.path.split(path)[1]
            ds_id, version_date1, stn_id, chunk_id, _, _ = path1.split('_')

            if ds_id in paths_dict:
                    paths_dict[ds_id].append(path)
            else:
                paths_dict[ds_id] = [path]

        ## Iterate through datasets
        rc_paths = []

        for ds_id, stn_files in paths_dict.items():

            if ds_id in old_versions:
                old_versions1 = [v['version_date'] for v in old_versions[ds_id]]
            else:
                old_versions1 = []

            ## Get the old results chunks file
            if self.max_version_date in old_versions1:
                old_rc_data = s3.get_remote_results_chunks(self.bucket, dataset_id=ds_id, version_date=self.max_version_date, s3=None, connection_config=self.connection_config, public_url=self.public_url,  system_version=self.system_version)
            elif add_old and (len(old_versions1) > 0):
                previous_version_date = old_versions1[-1]
                old_rc_data = s3.get_remote_results_chunks(self.bucket, dataset_id=ds_id, version_date=previous_version_date, s3=None, connection_config=self.connection_config, public_url=self.public_url,  system_version=self.system_version)
            else:
                old_rc_data = None

            ## Run through all files
            rc_path = processing.update_results_chunks(stn_files, self.preprocessed_path, old_rc_data, max_workers)
            rc_paths.append(rc_path)

        self.results_chunks_paths = rc_paths

        ## diagnostic log
        self.diagnostics['update_results_chunks'] = {'pass': True}

        return rc_paths


    def _update_stations(self, results_paths, old_versions, max_workers=4):
        """

        """
        ## Checks
        misc.diagnostic_check(self.diagnostics, 'update_results_chunks')

        add_old = self._add_old

        ## Organise the paths
        paths_dict = {}
        for path in list(set(results_paths)):
            path1 = os.path.split(path)[1]
            ds_id, version_date1, stn_id, chunk_id, _, _ = path1.split('_')

            if ds_id in paths_dict:
                    paths_dict[ds_id].append(path)
            else:
                paths_dict[ds_id] = [path]

        rc_paths = self.results_chunks_paths.copy()

        rc_path_dict = {}
        for path in rc_paths:
            path1 = os.path.split(path)[1]
            ds_id = path1.split('_')[0]
            rc_path_dict[ds_id] = path

        ## Iterate through datasets
        stn_paths = []

        for ds_id, data_paths in paths_dict.items():
            rc_path = rc_path_dict[ds_id]

            if ds_id in old_versions:
                old_versions1 = [v['version_date'] for v in old_versions[ds_id]]
            else:
                old_versions1 = []

            ## Get the old results chunks file
            if self.max_version_date in old_versions1:
                old_stns_data = s3.get_remote_stations(self.bucket, dataset_id=ds_id, version_date=self.max_version_date, s3=None, connection_config=self.connection_config, public_url=self.public_url,  system_version=self.system_version)
            elif add_old and (len(old_versions1) > 0):
                previous_version_date = old_versions1[-1]
                old_stns_data = s3.get_remote_stations(self.bucket, dataset_id=ds_id, version_date=previous_version_date, s3=None, connection_config=self.connection_config, public_url=self.public_url,  system_version=self.system_version)
            else:
                old_stns_data = None

            stn_path = processing.update_stations(data_paths, rc_path, self.preprocessed_path, old_stns_data, max_workers)
            stn_paths.append(stn_path)

        self.stations_paths = stn_paths

        ## diagnostic log
        self.diagnostics['update_stations'] = {'pass': True}

        return stn_paths


    def _update_versions(self, old_versions, max_workers=4):
        """

        """
        ## Checks
        misc.diagnostic_check(self.diagnostics, 'update_stations')

        ## Determine what datasets are updated
        dataset_ids = []
        for d in self.results_chunks_paths:
            ds_id = os.path.split(d)[1].split('_')[0]
            dataset_ids.append(ds_id)

        ## Run versions update
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
            futures = []
            for dataset_id in dataset_ids:
                version_data1 = self.version_dict[dataset_id]

                ## Get the versions
                if dataset_id in old_versions:
                    old_versions1 = old_versions[dataset_id]
                else:
                    old_versions1 = None

                f = executor.submit(processing.update_versions, version_data1, self.preprocessed_path, old_versions1)
                futures.append(f)

            runs = concurrent.futures.wait(futures)

        versions_paths = [r.result() for r in runs[0]]

        self.versions_paths = versions_paths

        ## diagnostic log
        self.diagnostics['update_versions'] = {'pass': True}

        return versions_paths


    def _update_datasets(self):
        """

        """
        ## Checks
        misc.diagnostic_check(self.diagnostics, 'update_versions')

        ## Save the individual datasets
        ds_paths = []
        for stns_path in self.stations_paths:
            ds_id = os.path.split(stns_path)[1].split('_')[0]
            dataset = self.datasets[ds_id]
            ds_path = processing.update_dataset(dataset, self.preprocessed_path, stns_path, self.system_version)
            ds_paths.append(ds_path)

        ## Process the agg dataset file
        # Get the old file
        dss_key = tdm.utils.key_patterns[self.system_version]['datasets']

        dss_obj = get_object_s3(dss_key, bucket=self.bucket, connection_config=self.connection_config, public_url=self.public_url, counter=2)

        if dss_obj is None:
            old_datasets = None
        else:
            old_datasets = read_json_zstd(dss_obj)

        # Process and save the new file
        dss_path = processing.update_dataset_agg(ds_paths, self.preprocessed_path, old_datasets)

        ## diagnostic log
        self.diagnostics['update_datasets'] = {'pass': True}

        return ds_paths


    def _upload_final_objects(self, threads=60):
        """

        """
        ## Determine all the different files to upload
        rc_paths = glob.glob(os.path.join(self.preprocessed_path, '*results_chunks.json.zst'))

        if len(rc_paths) > 0:

            results_paths = glob.glob(os.path.join(self.preprocessed_path, '*results.nc.zst'))
            stns_paths = glob.glob(os.path.join(self.preprocessed_path, '*stations.json.zst'))
            v_paths = glob.glob(os.path.join(self.preprocessed_path, '*versions.json.zst'))
            ds_paths = glob.glob(os.path.join(self.preprocessed_path, '*dataset.json.zst'))
            dss_path = glob.glob(os.path.join(self.preprocessed_path, 'datasets.json.zst'))

            ## Checks
            misc.diagnostic_check(self.diagnostics, 'update_datasets')

            # ds_set = set()
            # for p in results_paths:
            #     ds_id = os.path.split(p)[1].split('_')[0]
            #     ds_set.add(ds_id)

            if not (len(rc_paths) == len(stns_paths) == len(ds_paths) == len(v_paths)):
                raise ValueError('The number of auxillary files do not match up.')

            if len(dss_path) != 1:
                raise ValueError('There must be one datasets.json.zst file.')

            ## Prepare files to be uploaded
            all_paths = results_paths.copy()
            all_paths.extend(rc_paths)
            all_paths.extend(stns_paths)
            all_paths.extend(v_paths)
            all_paths.extend(ds_paths)
            all_paths.extend(dss_path)
            random.shuffle(all_paths)

            client = s3_client(self.connection_config, max_pool_connections=threads)

            s3_list = []
            append = s3_list.append
            for path in all_paths:
                dict1 = processing.prepare_file_for_s3(path, client, self.bucket, self.system_version)
                append(dict1)

            ## Iterate through the files
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []

                for s3_dict in s3_list:
                    f = executor.submit(s3.put_file_s3, **s3_dict)
                    futures.append(f)

                runs = concurrent.futures.wait(futures)

            resp = [r.result() for r in runs[0]]

        else:
            print('There seems to be no useful files in the results path. Nothing will get uploaded and any files in the path will be removed.')
            resp = None

        ## Remove all files in the results path
        path1 = pathlib.Path(self.preprocessed_path)
        for path in path1.glob('*'):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                os.remove(path)

        return resp


    def update_final_objects(self, results_paths, threads=60, max_workers=4):
        """

        """
        if len(results_paths) > 0:

            print('-- Processing results...')
            results_paths1 = self._save_new_results(results_paths, max_workers=max_workers)
        else:
            results_paths1 = []

        if len(results_paths1) > 0:

            ## Determine the chunks diffs
            if isinstance(self.public_url, str):
                remote1 = {'bucket': self.bucket, 'public_url': self.public_url, 'version': self.system_version}
            else:
                remote1 = {'bucket': self.bucket, 'connection_config': self.connection_config, 'version': self.system_version}

            results_paths_set = set(results_paths1)

            rc_diffs = self._determine_results_chunks_diffs(list(results_paths_set), remote1, add_old=self._add_old, max_workers=max_workers)

            print('-- Check and update conflicting results chunks...')
            results_paths_new = self._update_conflicting_results(results_paths, rc_diffs, threads=threads, max_workers=max_workers)

            if len(results_paths_new) > 0:

                ## Get old versions
                ds_ids = set()
                for path in list(set(results_paths_new)):
                    path1 = os.path.split(path)[1]
                    ds_id, version_date1, stn_id, chunk_id, _, _ = path1.split('_')
                    ds_ids.add(ds_id)

                old_versions = s3.get_versions(list(ds_ids), self.bucket, connection_config=self.connection_config, public_url=self.public_url, system_version=self.system_version)

                print('-- Updating the results chunks...')
                rc_paths = self._update_results_chunks(results_paths_new, rc_diffs, old_versions, max_workers)

                print('-- Updating the stations...')
                stns_paths = self._update_stations(results_paths_new, old_versions, max_workers)

                print('-- Updating the versions...')
                versions_paths = self._update_versions(old_versions, max_workers)

                print('-- Updating the datasets...')
                ds_paths = self._update_datasets()

                print('-- Uploading final objects...')
                resp = self._upload_final_objects(threads=threads)

            else:
                print('No results to update')
                resp = None

        else:
            print('No results to update')
            resp = None

        print('-- Tethys has been successfully updated!')

        return resp


    def _reset_auxillary_objects(self, dataset_id, threads=80, max_workers=4):
        """

        """
        if dataset_id not in self.datasets:
            raise ValueError('{} dataset_id not available.'.format(dataset_id))

        ## Create dir for existing data
        existing_data_path = os.path.join(self.preprocessed_path, 'existing_data')
        os.makedirs(existing_data_path, exist_ok=True)

        ## Determine all of the object to download
        vd = self.max_version_date
        vd_key = make_run_date_key(vd)

        key_prefix = tdm.utils.key_patterns[self.system_version]['results'].split('{station_id}')[0].format(dataset_id=dataset_id, version_date=vd_key)

        client = s3_client(self.connection_config, threads)

        obj_list1 = s3.list_objects_s3(client, self.bucket, key_prefix)
        obj_list1 = obj_list1[obj_list1.Key.str.contains('results')].copy()

        ## Download data
        print('-- Downloading all results chunks ({})...'.format(len(obj_list1)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []

            for key in obj_list1.Key.tolist():
                f = executor.submit(s3.download_results, key, existing_data_path, self.bucket, client, public_url=self.public_url)
                futures.append(f)

            runs = concurrent.futures.wait(futures)

        new_paths = [r.result() for r in runs[0]]

        ## Keep the old_version for later
        old_versions = copy.deepcopy(self.old_versions)
        self.old_versions = {}

        ## Apply fake completion
        self.diagnostics['update_conflicting_results'] = {'pass': True}
        self.diagnostics['save_new_results'] = {'pass': True}

        ## Update aux files
        print('-- Updating the results chunks...')
        rc_paths = self._update_results_chunks(new_paths, None, max_workers)

        print('-- Updating the stations...')
        stns_paths = self._update_stations(new_paths, max_workers)

        print('-- Updating the versions...')
        self.old_versions = old_versions
        versions_paths = self._update_versions(1)

        print('-- Updating the datasets...')
        ds_paths = self._update_datasets()

        print('-- Uploading final objects...')
        resp = self._upload_final_objects(threads=threads)

        return resp






































################################
### Testing


   # def init_ray(self, num_cpus=1, include_dashboard=False, configure_logging=False, **kwargs):
    #     """

    #     """
    #     if ray.is_initialized():
    #         ray.shutdown()

    #     ray.init(num_cpus=num_cpus, include_dashboard=include_dashboard, configure_logging=configure_logging, **kwargs)

    #     @ray.remote
    #     def _load_result(dataset, result, run_date_key, other_attrs, discrete, other_closed, sum_closed, other_encoding):
    #         """

    #         """
    #         out1 = processing.prepare_results_v02(dataset, result, run_date_key, sum_closed=sum_closed, other_closed=other_closed, discrete=discrete, other_attrs=other_attrs, other_encoding=other_encoding)

    #         return out1

    #     self._load_result = _load_result
    #     self._obj_refs = []


    # def shutdown_ray(self):
    #     ray.shutdown()


    # def load_results(self, results, sum_closed='right', other_closed='left', discrete=True, other_attrs=None, other_encoding=None, run_date=None):
    #     """

    #     """
    #     ## Dataset checks
    #     # ds_ids = list(results.keys())

    #     if isinstance(run_date, str):
    #         run_date_key = misc.make_run_date_key(run_date)
    #     else:
    #         run_date_key = self.max_run_date_key

    #     r1 = [self._load_result.remote(self.datasets[r['dataset_id']], r['result'], run_date_key, other_attrs, discrete, other_closed, sum_closed, other_encoding) for r in results]
    #     # r2 = ray.get(r1)

    #     self._obj_refs.extend(r1)
