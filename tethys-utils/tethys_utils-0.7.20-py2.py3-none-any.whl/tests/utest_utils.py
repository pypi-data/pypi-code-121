# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 09:25:41 2019

@author: michaelek
"""
import pytest
from tethys_utils import *
from tethysts import Tethys
import pandas as pd
# from tethys_utils.datasets import get_path

pd.options.display.max_columns = 10


###############################################
### Parameters

# remote = {'bucket': 'nz-open-modelling-consortium', 'connection_config': 'https://b2.nzrivers.xyz', 'version': 3}
remote = {'bucket': 'ecan-env-monitoring', 'connection_config': 'https://b2.tethys-ts.xyz', 'version': 2}

attrs = {'quality_code': {'standard_name': 'quality_flag',
  'long_name': 'NEMS quality code',
  'references': 'https://www.lawa.org.nz/media/16580/nems-quality-code-schema-2013-06-1-.pdf'},
  'well_depth': {'units': 'm'},
  'well_diameter': {'units': 'mm'},
  'well_screens': {'units': ''},
  'well_top_screen': {'units': 'm'},
  'well_bottom_screen': {'units': 'm'},
  }

encoding = {'quality_code': {'dtype': 'int16', '_FillValue': -9999},
  'well_depth': {'dtype': 'int32', '_FillValue': -99999, 'scale_factor': 0.1},
  'well_diameter': {'dtype': 'int32',
   '_FillValue': -99999,
   'scale_factor': 0.1},
  'well_screens': {'dtype': 'int16', '_FillValue': -9999},
  'well_top_screen': {'dtype': 'int32',
   '_FillValue': -99999,
   'scale_factor': 0.1},
  'well_bottom_screen': {'dtype': 'int32',
   '_FillValue': -99999,
   'scale_factor': 0.1},
  'groundwater_depth': {'scale_factor': 0.001,
     'dtype': 'int32',
     '_FillValue': 9999}}

ds_id = 'f98dfaefbc15f045f900e4b9'
station_id = 'fff111e6e8e652b0804a21b4'
parameter = 'groundwater_depth'

########################################
### Tests

self = Tethys([remote])

stns = self.get_stations(ds_id)

results = self.get_results(ds_id, station_id)
data = results.drop(['lat', 'lon'])

param_attrs = data[parameter].attrs.copy()
_ = [param_attrs.pop(p) for p, v in data[parameter].attrs.items() if p in ['dataset_id', 'ancillary_variables', 'result_type']]
param_attrs['spatial_distribution'] = 'sparse'
param_attrs['geometry_type'] = 'Point'
param_attrs['grouping'] = 'none'
param_attrs['parent_datasets'] = ['rrrrrrr', 'ttttttt']

attrs[parameter] = param_attrs

res3 = package_xarray(data, parameter, attrs, encoding)



def test_read_pkl_zstd():
    df1 = read_pkl_zstd(d_path1)

    assert df1.shape == (20000, 7)



def test_write_pkl_zstd():
    p_df1 = write_pkl_zstd(df1)
    len1 = round(len(p_df1), -3)

    assert (len1 < 200000) and (len1 > 100000)


def test_df_to_xarray():
    p_ds1 = df_to_xarray(df1, nc_type, param_name, attrs, encoding, run_date_key, ancillary_variables, compression)
    len2 = round(len(p_ds1), -3)

    ds1 = df_to_xarray(df1, nc_type, param_name, attrs, encoding, run_date_key, ancillary_variables)

    assert (len(ds1) == 6) and (len2 < 30000) and (len2 > 20000)




# @pytest.mark.parametrize('input_sites', [input_sites1, input_sites2, input_sites3])
# def test_nat(input_sites):
#     f1 = FlowNat(from_date, to_date, input_sites=input_sites)
#
#     nat_flow = f1.naturalisation()
#
#     assert (len(f1.summ) >= 1) & (len(nat_flow) > 2900)
