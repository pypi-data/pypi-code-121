"""
Created on 2021-04-27.

@author: Mike K
"""
from tethysts import Tethys
import pandas as pd
import os
import pytest
import tethys_utils as tu
import yaml
import copy
import requests
import io
from time import sleep

pd.options.display.max_columns = 10

##############################################
### Parameters

base_dir = os.path.realpath(os.path.dirname(__file__))

with open(os.path.join(base_dir, 'parameters-test.yml')) as param:
    param = yaml.safe_load(param)

public_url = param['source']['public_url']
s3_remote = param['remote']['s3']

remote = {'public_url': public_url, 'bucket': s3_remote['bucket'], 'version': 4}

ds_id = 'c3a09c8a5da175897916e8e8'

run_input_list = [{'run': 1, 'stns': ['219510'], 'period': '2_Days', 'version_date': '2022-05-01', 'add_old': True},
            {'run': 2, 'stns': ['219510'], 'period': '2_Days', 'version_date': '2022-05-01', 'add_old': True},
            {'run': 3, 'stns': ['219510'], 'period': '1_Week', 'version_date': '2022-05-01', 'add_old': True},
            {'run': 4, 'stns': ['219910'], 'period': '2_Days', 'version_date': '2022-05-01', 'add_old': True},
            {'run': 5, 'stns': ['320010'], 'period': '2_Days', 'version_date': '2022-05-02', 'add_old': True},
            {'run': 6, 'stns': ['320010'], 'period': '1_Week', 'version_date': '2022-05-03', 'add_old': False}]

assert_list = [{'n_stns': 1, 'time_len': 10},
               {'n_stns': 1, 'time_len': 10},
               {'n_stns': 1, 'time_len': 100},
               {'n_stns': 2, 'time_len': 10},
               {'n_stns': 3, 'time_len': 10},
               {'n_stns': 1, 'time_len': 100}]

#######################################
### Functions


def titan_time_series(stns, period, version_date, add_old):

    #####################################
    ### Parameters
    print('load parameters')

    ts_local_tz = 'Etc/GMT-12'

    source = param['source']
    system_version = source['system_version']
    datasets = source['datasets'].copy()
    public_url = source['public_url']
    s3_remote = param['remote']['s3']
    # period = source['period']
    temp_path = source['output_path']
    # version_data = param['source']['results_version']
    version_data = {'version_date': version_date}
    stn_data_source = source['stn_data']

    #####################################
    ### Do the work

    ### Initalize
    run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)

    print('Start:')
    print(run_date)

    ts = tu.TimeSeries(temp_path=temp_path, add_old=add_old)

    ts.status_checks(s3_remote['connection_config'], s3_remote['bucket'], public_url)

    ts.load_dataset_metadata(datasets)

    version_dict = ts.process_versions(version_data)

    results_paths2 = []

    for meas, ds in datasets.items():
        print('----- Starting new dataset group -----')
        print(meas)

        ### Pull out stations
        # remote = source['site_data'][meas].copy()
        # remote_ds = remote.pop('dataset_id')
        stn_remote = copy.deepcopy(stn_data_source[meas])
        stn_ds_id = stn_remote.pop('dataset_id')
        t1 = Tethys([stn_remote])
        # remote_ds = ds[0]['dataset_id']

        remote_stns = t1.get_stations(stn_ds_id)
        remote_stns1 = [s for s in remote_stns if s['ref'] in stns]

        for s in remote_stns1:
            for e in ['dimensions', 'heights', 'time_range', 'modified_date', 'content_length']:
                if e in s:
                    s.pop(e)

        stns1, attrs = tu.processing.stations_dict_to_df(remote_stns1)
        if 'altitude' in stns1:
            stns1['altitude'] = pd.to_numeric(stns1['altitude'])

        ####################################
        ### Get ts data

        for stn in stns1.to_dict(orient="records"):
            print(stn['name'])

            url = source['data_url'][meas].format(ref=stn['ref'], period=period)

            resp = requests.get(url)

            resp.raise_for_status()

            b_io = io.BytesIO(resp.content)

            data1 = pd.read_csv(b_io, compression='zip')
            data1.columns = ['ref', 'time', datasets[meas][0]['parameter']]
            data1.drop('ref', axis=1, inplace=True)
            data1['time'] = pd.to_datetime(data1['time'].str.replace('.', '', regex=False).str.upper(), format='%d/%m/%Y %I:%M:%S %p').dt.round('T')
            data1['height'] = 0
            data1['time'] = data1['time'].dt.tz_localize(ts_local_tz).dt.tz_convert('utc').dt.tz_localize(None)

            data2 = ts.combine_obs_stn_data(data1, stn, mod_date=False)

            ###########################################
            ## Package up into the data_dict
            if not data1.empty:
                for ds in datasets[meas]:
                    results_paths1 = ts.save_preprocessed_results(data2, ds['dataset_id'])
                    results_paths2.extend(results_paths1)

    ########################################
    ### Save results and stations
    # print('-- Processing results')
    # results_paths3 = ts.save_new_results(results_paths2, max_workers=1)

    # print('-- Updating conflicting results')
    # updated_results = ts.update_conflicting_results(results_paths3, threads=60, max_workers=1)

    # ts.update_auxiliary_objects(updated_results, max_workers=1)

    # print('-- Uploading final objects')
    # resp = ts.upload_final_objects(threads=60)

    resp = ts.update_final_objects(results_paths2, threads=60, max_workers=1)

    ### Timings
    end_run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)

    print('-- Finished!')
    print(end_run_date)



######################################
### Testing


# t1 = Tethys([remote])

# assert len(t1.datasets) == 1

# vs = t1.get_versions(ds_id)

# stns1 = t1.get_stations(ds_id, version_date='2022-05-02T00:00:00')

# assert len(stns1) == 3

# time_len = stns1[-1]['dimensions']['time']

# assert time_len > 10

# r1 = t1.get_results(ds_id, stns1[0]['station_id'])

# assert r1.dims['time'] == time_len



@pytest.mark.parametrize('run_input', run_input_list)
def test_time_series(run_input):
    """

    """
    run_index = run_input.pop('run') - 1
    titan_time_series(**run_input)

    sleep(5)

    ## Tests
    assert_dict = assert_list[run_index]

    t1 = Tethys([remote])

    assert len(t1.datasets) == 1

    stns1 = t1.get_stations(ds_id)

    assert len(stns1) == assert_dict['n_stns']

    time_len = stns1[-1]['dimensions']['time']

    assert time_len > assert_dict['time_len']

    r1 = t1.get_results(ds_id, stns1[-1]['station_id'])

    assert r1.dims['time'] == time_len


def test_delete_dataset():
    print('-- Remove dataset')
    rem_keys = tu.s3.delete_dataset_s3(s3_remote['connection_config'], s3_remote['bucket'], ds_id)

    assert len(rem_keys) > 1

## initialise for the rest of the tests
# t1 = Tethys([remote3])


# @pytest.mark.parametrize('output', outputs)
# def test_get_results(output):
#     data1 = t1.get_results(dataset_id, station_ids, squeeze_dims=True, output=output)

#     if output == 'xarray':
#         assert len(data1.time) > 90
#     elif output == 'dict':
#         assert len(data1['coords']['time']['data']) > 90
#     elif output == 'json':
#         assert len(data1) > 90


# def test_get_nearest_station1():
#     s1 = t1.get_stations(dataset_id, geometry1)

#     assert len(s1) == 1


# def test_get_nearest_station2():
#     s2 = t1.get_stations(dataset_id, lat=lat, lon=lon)

#     assert len(s2) == 1


# def test_get_intersection_stations1():
#     s3 = t1.get_stations(dataset_id, lat=lat, lon=lon, distance=distance)

#     assert len(s3) >= 2


# def test_get_nearest_results1():
#     s1 = t1.get_results(dataset_id, geometry=geometry1)

#     assert len(s1) > 1


# def test_get_nearest_results2():
#     s2 = t1.get_results(dataset_id, lat=lat, lon=lon)

#     assert len(s2) > 1


# def test_get_intersection_results1():
#     s3 = t1.get_results(dataset_id, lat=lat, lon=lon, distance=distance)
#
#     assert len(s3) > 1



# with open(obj, 'rb') as p:
#     dctx = zstd.ZstdDecompressor()
#     obj00 = p.read()
#     obj1 = dctx.decompress(obj00, max_output_size=s1)
#     # obj0 = p.read()

# obj0 = read_pkl_zstd(obj)

# obj1 = tu.misc.write_pkl_zstd(obj0)


# with open(obj, 'rb') as p:
#     dctx = zstd.ZstdDecompressor()
#     obj1 = dctx.decompress(p.read())















