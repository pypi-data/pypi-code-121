#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  4 14:38:14 2022

@author: mike
"""
import os
import numpy as np
import xarray as xr
import pandas as pd
from tethys_utils import misc, s3, processing, titan
from tethysts.utils import s3_client, get_object_s3, read_json_zstd, read_pkl_zstd, download_results, create_public_s3_url
import tethys_data_models as tdm
from typing import List, Optional, Dict, Union
import uuid
import pandas as pd
from pydantic import HttpUrl
import pathlib
from time import sleep

##############################################
### Parameters

preprocessed_file_str = '{ds_id}_{file_id}.nc.zst'

agg_stat_mapping = {'mean': 'mean', 'cumulative': 'sum', 'instantaneous': 'first', 'maximum': 'max', 'median': 'median', 'minimum': 'min', 'mode': 'mode', 'standard_deviation': 'std', 'incremental': 'cumsum'}

tz_str = 'Etc/GMT{0:+}'


############################################
### Main class


class TimeSeries(titan.Titan):
    """

    """
    @staticmethod
    def process_sparse_stations_from_df(stns, precision=7):
        """
        Function that takes a stns dataframe of station data and converts it to an Xarray Dataset for Tethys. This is ultimately meant to be combined with the time series data for futher processing. If a geometry column is provided, it must be as a geojson-type dict (not a geopandas column).

        Parameters
        ----------
        stns: pd.DataFrame
            DataFrame of the station data. It must have lat and lon columns at least.
        precision: int
            The decimal degrees precision of the coordinates.

        Returns
        -------
        xarray dataset
            of the station data.

        """
        stns = processing.process_sparse_stations_from_df(stns, precision=precision)

        return stns


    @staticmethod
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
        r1 = processing.combine_obs_stn_data(ts_data, stn_data, mod_date=mod_date)

        return r1


    def resample_time_series(self, df, dataset_id, sum_closed='right', other_closed='left', discrete=False):
        """
        Method that resamples a single station's time series results. There must be at least one column called "time" and another column with the parameter name.

        Parameters
        ----------
        df: pd.DataFrame
            Of the results data.
        dataset_id: str
            The dataset_id associated with the results.
        sum_closed: str
            Either right or left and applied to results listed as cumulative.
        other_closed: str
            Either right or left and applied to results not listed as cumulative.
        discrete: bool
            Does the results represent instantaneous (discrete) values?

        Returns
        -------
        pd.DataFrame
        """
        dataset = self.datasets[dataset_id]
        freq_code = dataset['frequency_interval']
        agg_stat = dataset['aggregation_statistic']
        parameter = dataset['parameter']
        utc_offset = dataset['utc_offset']

        df1 = df.copy()

        # check columns
        cols = df1.columns

        if 'time' not in cols:
            raise ValueError('time must be a column.')
        if parameter not in cols:
            raise ValueError(parameter + ' must be a column.')

        grp = []
        if 'station_id' in cols:
            grp.append('station_id')
        if 'height' in cols:
            grp.append('height')

        vars1 = [parameter] + ['time'] + grp

        ancillary_variables = [v for v in cols if (v not in vars1)]

        # main_vars = [parameter] + ancillary_variables

        # Convert times to local TZ if necessary
        if (not freq_code in ['None', 'T', 'H', '1H']) and (utc_offset != '0H'):
            t1 = int(utc_offset.split('H')[0])
            tz1 = tz_str.format(-t1)
            df1['time'] = df1['time'].dt.tz_localize('UTC').dt.tz_convert(tz1).dt.tz_localize(None)

        ## Aggregate data if necessary
        # Parameter
        if freq_code == 'None':
            data1 = df1.drop_duplicates(subset=['time']).sort_values('time')
        else:
            agg_fun = agg_stat_mapping[agg_stat]

            if agg_fun == 'sum':
                data0 = misc.grp_ts_agg(df1[vars1], grp, 'time', freq_code, agg_fun, closed=sum_closed)
            else:
                data0 = misc.grp_ts_agg(df1[vars1], grp, 'time', freq_code, agg_fun, discrete, closed=other_closed)

            # Ancillary variables
            av_list = [data0]
            for av in ancillary_variables:
                if 'quality_code' == av:
                    df1['quality_code'] = pd.to_numeric(df1['quality_code'], errors='coerce', downcast='integer')
                    qual1 = misc.grp_ts_agg(df1[['time'] + grp + ['quality_code']], grp, 'time', freq_code, 'min')
                    av_list.append(qual1)
                else:
                    av1 = misc.grp_ts_agg(df1[['time'] + grp + [av]], grp, 'time', freq_code, 'max')
                    av_list.append(av1)

            # Put the data together
            data1 = pd.concat(av_list, axis=1).reset_index().sort_values('time')

        # Convert time back to UTC if necessary
        if (not freq_code in ['None', 'T', 'H', '1H']) and (utc_offset != '0H'):
            data1['time'] = data1['time'].dt.tz_localize(tz1).dt.tz_convert('utc').dt.tz_localize(None)

        return data1


    def save_preprocessed_results(self, data: Union[List[xr.Dataset], xr.Dataset], dataset_id: str):
        """
        Method to save preprocessed results xarray datasets to netcdf files in the temp_path. The results must have the standard dimensions, geometry caclulated, appropriate parameter names, and station data.
        """
        ## Prepare
        dataset1 = self.datasets[dataset_id]
        result_type = dataset1['result_type']
        param = dataset1['parameter']
        data_model = tdm.dataset.result_type_dict[result_type]
        dims = set(data_model.schema()['properties'].keys())

        if isinstance(data, xr.Dataset):
            data_list = [data]
        else:
            data_list = data

        ## Run checks
        misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

        _ = [data_model(**d.dims) for d in data_list]

        for d in data_list:
            if not param in d:
                raise ValueError('The {param} valiable should be in the data if {ds_id} is the dataset_id.'.format(param=param, ds_id=dataset_id))

            d_dims = set(d[param].dims)
            if d_dims != dims:
                raise ValueError('The {param} valiable should contain the dims: {dims}.'.format(param=param, dims=dims))

        d_bool = [0 in dict(d.dims).values() for d in data_list]

        if any(d_bool):
            raise ValueError('Data has dimensions with 0 length. This would indicate some kind of empty data.')

        ## Save the data
        file_list = []
        for d in data_list:
            # print(str(d.ref.values[0]))

            ## Update the metadata
            d = processing.add_metadata_results(d, dataset1, self.max_version_date)

            file_id = uuid.uuid4().hex[:14]
            file_path = os.path.join(self.preprocessed_path, preprocessed_file_str.format(ds_id=dataset_id, file_id=file_id))

            misc.write_pkl_zstd(d.to_netcdf(), file_path)

            # Read the file back in to make sure it worked...
            # _ = xr.load_dataset(read_pkl_zstd(file_path))

            file_list.append(file_path)

        return file_list





























































