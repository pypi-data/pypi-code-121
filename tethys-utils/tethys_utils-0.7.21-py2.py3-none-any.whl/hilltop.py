"""

"""
import requests
import numpy as np
import pandas as pd
import xarray as xr
from time import sleep
import traceback
import tethys_utils as tu


##########################################################
### Functions for Hilltop data extraction


def convert_site_names(names, rem_m=True):
    """
    Function to convert water usage site names.
    """

    names1 = names.str.replace('[:\.]', '/')
#    names1.loc[names1 == 'L35183/580-M1'] = 'L35/183/580-M1' What to do with this one?
#    names1.loc[names1 == 'L370557-M1'] = 'L37/0557-M1'
#    names1.loc[names1 == 'L370557-M72'] = 'L37/0557-M72'
#    names1.loc[names1 == 'BENNETT K38/0190-M1'] = 'K38/0190-M1'
    names1 = names1.str.upper()
    if rem_m:
        list_names1 = names1.str.findall('[A-Z]+\d*/\d+')
        names_len_bool = list_names1.apply(lambda x: len(x)) == 1
        names2 = names1.copy()
        names2[names_len_bool] = list_names1[names_len_bool].apply(lambda x: x[0])
        names2[~names_len_bool] = np.nan
    else:
        list_names1 = names1.str.findall('[A-Z]+\d*/\d+\s*-\s*M\d*')
        names_len_bool = list_names1.apply(lambda x: len(x)) == 1
        names2 = names1.copy()
        names2[names_len_bool] = list_names1[names_len_bool].apply(lambda x: x[0])
        names2[~names_len_bool] = np.nan

    return names2


def get_hilltop_results(param, station_mtype_corrections=None, quality_codes=True, modified_date=True, local_tz='Etc/GMT-12', add_ref_as_name=False, from_offset=None, threads=80, max_workers=1):
    """

    """
    # import requests
    from hilltoppy import web_service as ws

    try:
        run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)

        print('Start:')
        print(run_date)

        ### Read in parameters
        base_url = param['source']['api_endpoint']
        hts = param['source']['hts']

        source = param['source']
        system_version = source['system_version']
        datasets = source['datasets'].copy()
        s3_remote = param['remote']['s3']
        temp_path = source['output_path']

        if 'results_version' in param['source']:
            version_data = param['source']['results_version']
        else:
            run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)
            version_data = {'version_date': run_date}

        if 'public_url' in source:
            public_url = source['public_url']
        else:
            public_url = None


        ### Initalize
        if isinstance(from_offset, str):
            from_offset1 = pd.tseries.frequencies.to_offset(from_offset)
            old_date = (run_date - from_offset1).round('T')

        titan = tu.TimeSeries(temp_path=temp_path, add_old=True)

        titan.status_checks(s3_remote['connection_config'], s3_remote['bucket'], public_url)

        titan.load_dataset_metadata(datasets)

        version_dict = titan.process_versions(version_data)

        results_paths2 = []

        for meas in datasets:
            print('----- Starting new dataset group -----')
            print(meas)

            ### Pull out stations
            stns1 = ws.site_list(base_url, hts, location='LatLong') # There's a problem with Hilltop that requires running the site list without a measurement first...
            stns1 = ws.site_list(base_url, hts, location='LatLong', measurement=meas)
            stns2 = stns1[(stns1.lat > -47.5) & (stns1.lat < -34) & (stns1.lon > 166) & (stns1.lon < 179)].dropna().copy()
            stns2.rename(columns={'SiteName': 'ref'}, inplace=True)

            if add_ref_as_name:
                stns2['name'] = stns2['ref']

            ## Process stations
            stns3 = titan.process_sparse_stations_from_df(stns2)

            ### Get the Hilltop measurement types
            print('-- Running through station/measurement combos')

            mtypes_list = []
            for s in stns3.ref.values:
                print(s)
                try:
                    meas1 = ws.measurement_list(base_url, hts, s)
                except:
                    print('** station is bad')
                mtypes_list.append(meas1)
            mtypes_df = pd.concat(mtypes_list).reset_index()
            mtypes_df = mtypes_df[mtypes_df.Measurement == meas].rename(columns={'Site': 'ref'})
            mtypes_df = pd.merge(mtypes_df, stns3.to_dataframe().reset_index(), on='ref')

            ## Limit data based on the oldest_data parameter if set
            if isinstance(from_offset, str):
                mtypes_df = mtypes_df[mtypes_df.To > old_date].copy()
                mtypes_df.loc[mtypes_df['From'] < old_date, 'From'] = old_date

            ## Make corrections to mtypes
            # mtypes_df['corrections'] = False

            if station_mtype_corrections is not None:
                for i, f in station_mtype_corrections.items():
                    mtypes_df.loc[(mtypes_df.ref == i[0]) & (mtypes_df.Measurement == i[1]), 'From'] = f
                    # mtypes_df.loc[(mtypes_df.ref == i[0]) & (mtypes_df.Measurement == i[1]), 'corrections'] = True

            if not mtypes_df.empty:

                ## Make sure there are no geometry duplicates
                mtypes_df['days'] = (mtypes_df.To - mtypes_df.From).dt.days
                mtypes_df = mtypes_df.sort_values(['geometry', 'days'], ascending=False)
                mtypes_df = mtypes_df.drop_duplicates(['geometry'], keep='first')

                # stns3 = stns3.where(stns3.station_id.isin(mtypes_df.station_id), drop=True)

                ##  Iterate through each stn
                print('-- Iterate through each station')
                for i, row in mtypes_df.iterrows():
                    print(row.ref)

                    parameter = datasets[meas][0]['parameter']

                    ## Get the station data
                    stn = stns3.sel(geometry=row.geometry)

                    if len(dict(stn.dims)) > 0:
                        stn = stn.isel(geometry=0)

                    stn = stn.expand_dims('geometry')

                    ## Get the data out
                    # print('- Extracting data...')

                    ts_list = []
                    bad_error = False

                    ## Break up the requests into 3 year chunks
                    time_diff = int((row.To - row.From).days/365)

                    if time_diff <= 3:
                        dates1 = [row.From, row.To]
                    else:
                        dates1 = list(pd.date_range(row.From, row.To, freq='3Y'))
                        dates1[0] = row.From
                        dates1.append(row.To)

                    for i, to_date in enumerate(dates1[1:]):
                        from_date = dates1[i]

                        timer = 5
                        while timer > 0:
                            try:
                                # sleep(1)
                                if row.Measurement == 'Abstraction Volume':
                                    ts_data0 = ws.get_data(base_url, hts, row.ref, row.Measurement, from_date=str(from_date), to_date=str(to_date), agg_method='Total', agg_interval='1 day')[1:]
                                else:
                                    ts_data0 = ws.get_data(base_url, hts, row.ref, row.Measurement, from_date=str(from_date), to_date=str(to_date), quality_codes=quality_codes, dtl_method='half')

                                ts_list.append(ts_data0)
                                break
                            except requests.exceptions.ConnectionError as err:
                                print(row.ref + ' and ' + row.Measurement + ' error: ' + str(err))
                                timer = timer - 1
                                sleep(30)
                            except ValueError as err:
                                print(row.ref + ' and ' + row.Measurement + ' error: ' + str(err))
                                bad_error = True
                                break
                            except Exception as err:
                                print(str(err))
                                timer = timer - 1
                                sleep(30)

                            if timer == 0:
                                raise ValueError('The Hilltop request tried too many times...the server is probably down')

                    if bad_error:
                        continue

                    ## Pre-process time series data
                    ts_data1 = pd.concat(ts_list)
                    ts_data1 = ts_data1.reset_index().rename(columns={'DateTime': 'time', 'Value': parameter, 'QualityCode': 'quality_code'}).drop(['Site', 'Measurement'], axis=1)
                    ts_data1['time'] = ts_data1['time'].dt.round('T')
                    ts_data1 = ts_data1.drop_duplicates(subset=['time']).dropna(subset=[parameter]).sort_values('time').reset_index(drop=True)

                    if len(ts_data1) > 3:

                        if 'quality_code' in ts_data1:
                            ts_data1['quality_code'] = pd.to_numeric(ts_data1['quality_code'], downcast='integer')

                        ## Determine median freq
                        freq_int = (ts_data1['time'].astype(int)/1000000000).dropna()
                        freq_int_diff = freq_int.diff().dropna().astype(int)
                        median_freq_int_diff = int(freq_int_diff.median())

                        if median_freq_int_diff >= 86400:
                            data_freqs = ['None', 'W', 'D', '24H', 'M', 'Y']
                        elif median_freq_int_diff >= 3600:
                            data_freqs = ['None', 'D', 'H', 'W', 'M', 'Y']
                        else:
                            data_freqs = ['None', 'D', 'H', 'T', 'W', 'M', 'Y']

                        if (row['Measurement'] == 'Water Level') and (row['Units'] == 'mm'):
                            ts_data1[parameter] = pd.to_numeric(ts_data1[parameter].values, errors='ignore') * 0.001
                        else:
                            ts_data1[parameter] = pd.to_numeric(ts_data1[parameter].values, errors='ignore')

                        ts_data1['height'] = 0
                        ts_data1['time'] = ts_data1['time'].dt.tz_localize(local_tz).dt.tz_convert('UTC').dt.tz_localize(None)

                        ###########################################
                        ## Package up into the data_dict
                        if parameter in ['precipitation', 'water_use']:
                            discrete = False
                        else:
                            discrete = True

                        for ds in datasets[meas]:
                            freq = ds['frequency_interval']
                            dataset_id = ds['dataset_id']

                            freq1 = [f for f in data_freqs if f in freq]

                            if freq1:
                                tsdata3 = titan.resample_time_series(ts_data1, dataset_id, discrete=discrete)

                                obs4 = titan.combine_obs_stn_data(tsdata3, stn, mod_date=modified_date)
                                results_paths1 = titan.save_preprocessed_results(obs4, dataset_id)
                                results_paths2.extend(results_paths1)

                        ## Dump the object from memory so that they do not keep adding up
                        ts_data1 = pd.DataFrame()
                        tsdata3 = pd.DataFrame()
                        obs4 = xr.Dataset()
                        del ts_data1
                        del tsdata3
                        del obs4

        ########################################
        ### Save results and stations
        resp = titan.update_final_objects(results_paths2, threads=threads, max_workers=max_workers)

        ### Timings
        end_run_date = pd.Timestamp.today(tz='utc').round('s').tz_localize(None)

        print('-- Finished!')
        print(end_run_date)

    except Exception as err:
        # print(err)
        print(traceback.format_exc())
        tu.misc.email_msg(param['remote']['email']['sender_address'], param['remote']['email']['sender_password'], param['remote']['email']['receiver_address'], 'Failure on Hilltop extraction for ' + base_url + hts, traceback.format_exc(), param['remote']['email']['smtp_server'])




###################################################
### Testing

# for k, v in data_dict1.items():
#     print(k)
#     nc1 = xr.load_dataset(utils.read_pkl_zstd(v[0]))
#     print(nc1)




























