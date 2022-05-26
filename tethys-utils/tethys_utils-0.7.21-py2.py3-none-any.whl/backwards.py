#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 14:42:10 2022

@author: mike
"""
from tethys_utils.titan import Titan
from tethysts import Tethys
from time import sleep

################################################
### Functions


def copy_old_dataset_to_new(source_remote, dest_remote, dataset, version_data, temp_path, add_old, remove_station_id=True, max_workers=4):
    """

    """
    ## Get parameters
    if 'public_url' in source_remote:
        public_url = source_remote['public_url']
    else:
        public_url = None

    ## Initialize Titan
    print('-- Initialize Titan')
    titan = Titan(temp_path=temp_path, add_old=add_old)

    titan.status_checks(dest_remote['connection_config'], dest_remote['bucket'], public_url)
    titan.load_dataset_metadata([dataset])

    dataset_id = titan.dataset_list[0]['dataset_id']

    print('-- Access Tethys')
    tethys = Tethys([source_remote])
    stns = tethys.get_stations(dataset_id)
    if version_data is None:
        rv = tethys.get_versions(dataset_id)

        version_data = rv[-1]

    version_dict = titan.process_versions(version_data)

    ## Get old results
    print('-- Get old results')
    results_list = []
    for s in stns:
        pass
        r1 = tethys.get_results(dataset_id, s['station_id']).drop_duplicates('time')
        if remove_station_id:
            r1 = r1.drop('station_id', errors='ignore')

        r_list = titan.save_preprocessed_results(r1, dataset_id)
        results_list.extend(r_list)

    print('-- Process old results into new')
    new_paths11 = titan.save_new_results(results_list, correct_times=False, max_workers=max_workers)

    if add_old:
        new_paths11 = titan.update_conflicting_results(new_paths11, threads=80, max_workers=1)

    titan.update_auxiliary_objects(new_paths11, max_workers=max_workers)

    print('-- Uploading final objects')
    resp = titan.upload_final_objects(threads=100)
