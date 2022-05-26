# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 09:25:41 2019

@author: michaelek
"""
import glob
import numpy as np
import os
import yaml
# import pytest
import xarray as xr
import pandas as pd
# from tethys_cdsapi import Processor
import concurrent.futures
from time import time
import tethys_utils as tu
import requests
from tethysts import utils

pd.options.display.max_columns = 10


###############################################
### Parameters

base_dir = os.path.realpath(os.path.dirname(__file__))

with open(os.path.join(base_dir, 'parameters1.yml')) as param:
    param = yaml.safe_load(param)

source = param['source'].copy()
remote = param['remote']['s3']
public_url = source['public_url']
processing_code = source['processing_code']
connection_config = remote['connection_config']
bucket = remote['bucket']

datasets = source['datasets']
# parameter = datasets[0]['parameter']

data_path1 = '/media/sdb1/Data/ecmwf/era5-land/2m_temperature_2003-2013_reanalysis-era5-land.nc'
# data_path1 = '/media/sdb1/Data/ecmwf/era5-land/2m_temperature_2014-2020_reanalysis-era5-land.nc'
data_path2 = '/media/sdb1/Data/ecmwf/era5-land/2m_temperature_*.nc'
data_path4 = '/media/sdb1/Data/ecmwf/era5-land/2m_temperature_2003-2013_reanalysis-era5-land_*.nc'
data_path3 = '/media/sdb1/Data/ecmwf/era5-land/2m_temperature-test1.nc'
data_path4 = '/media/sdb1/Data/ecmwf/era5-land/test/*.nc'
data_path5 = '/media/sdb1/Data/ecmwf/era5-land/test/total_evaporation_1981-1991_reanalysis-era5-land.nc'
data_path = ['/media/sdb1/Data/ecmwf/era5-land/test/2m_temperature_*.nc', '/media/sdb1/Data/ecmwf/era5-land/test/total_evaporation_*.nc']
parameter_code = 'temp_at_2'

grid = data_path2

encoding = {'dtype': 'int16', '_FillValue': -9999, 'scale_factor': 0.01}

lat_dim_name = 'latitude'
lon_dim_name = 'longitude'
time_dim_name = 'time'
dataset_id = 'b2f6bdd8aa592dacb3b257c0'
samples = 900

########################################
### Tests


# def preprocessor(ds):
#     """

#     """
#     ds = ds.rename({'longitude': 'lon', 'latitude': 'lat', 't2m': 'temperature'})
#     ds = ds.assign_coords({'height': 2})
#     ds = ds.expand_dims('height')
#     ds['temperature'] = ds['temperature'] - 273.15
#     ds['temperature'].encoding = encoding

#     return ds

# p1 = Processor(data_path, parameter_code, False)
# ds1 = p1.build_dataset()


# self = Grid(datasets, remote, processing_code, public_url)

# self.load_data(data, parameter, height=2)

# block_test = self.determine_grid_block_size(starting_x_size=20, starting_y_size=20, increment=10, min_size=800, max_size=1100)

# x_size = block_test['x_size']
# y_size = block_test['y_size']

d
# ds = xr.open_dataset(data_path1)
ds = xr.open_mfdataset(data_path2, chunks={'time': 1}, parallel=True, preprocess=preprocessor)
ds = xr.open_mfdataset(data_path2, chunks={'time': 350639, 'lon': 1, 'lat': 1},  preprocess=preprocessor)

ds = xr.open_mfdataset(data_path1, chunks={'time': 1}, parallel=True)
ds = xr.open_mfdataset(data_path2, chunks={'longitude': 20, 'latitude': 20}, parallel=True)

ds = ds.rename({'longitude': 'lon', 'latitude': 'lat', 't2m': 'temperature'})
ds = ds.assign_coords({'height': 2})
ds = ds.expand_dims('height')
ds['temperature'] = ds['temperature'] - 273.15
ds['temperature'].encoding = encoding

da = ds.temperature

da = da.chunk({'lon': 12})

chunks = np.arange(0, 12*(124//12+1)+12, 12)

file_name_str = '{}_part_{:>02d}.nc'

for i, c in enumerate(chunks[:-1]):
    print(c)
    new_file_path = file_name_str.format(os.path.splitext(data_path1)[0], i+1)
    ds1 = da.isel(lon=slice(chunks[i], chunks[i+1]))
    ds1.to_netcdf(new_file_path)


ds = ds.chunk({'time': 1})
ds5 = ds.isel(height=0, time=0, drop=True)

grid = ds

x_size=20
y_size=20
n_intervals = 4
samples=10

# x_name='longitude'
# y_name = 'latitude'

# ds4 = xr.open_dataset(data_path3)

# chunks = {'time': 10, 'latitude': 10, 'longitude': 10}
# chunks = {'time': 10000, 'latitude': 10, 'longitude': 10}
chunks = {'time': 10000}

self = Processor()

ds_list = self.load_dataset_metadata(datasets)

grid1 = self.load_raw_grid(data_path2, lon_dim_name, lat_dim_name, time_dim_name, preprocessor=tu.grid.processors.era5_land.preprocessor)



self.save_processed_grid()


da.to_netcdf(data_path3)
ds.to_netcdf(data_path3)
delayed_obj = ds.to_netcdf(data_path3, compute=False, engine="netcdf4")

with ProgressBar():
    results = delayed_obj.compute()


ds3 = xr.open_mfdataset(data_path4)


nc_files1 = glob.glob(data_path2)
nc_files1.sort()

base_path = os.path.split(data_path2)[0]

for f in nc_files1:
    print(f)
    ds = xr.open_mfdataset(f, chunks={'longitude': 12})

    ds = ds.rename({'longitude': 'lon', 'latitude': 'lat', 't2m': 'temperature'})
    ds = ds.assign_coords({'height': 2})
    ds = ds.expand_dims('height')
    ds['temperature'] = ds['temperature'] - 273.15
    ds['temperature'].encoding = encoding

    chunks = np.arange(0, 12*(124//12+1)+12, 12)

    file_name_str = '{}_part_{:>02d}.nc'

    for i, c in enumerate(chunks[:-1]):
        print(c)
        file_name = os.path.splitext(os.path.split(f)[1])[0]
        new_file_path = file_name_str.format(os.path.join(base_path, 'temp', file_name), i+1)
        ds1 = ds.isel(lon=slice(chunks[i], chunks[i+1]))
        ds1.to_netcdf(new_file_path)
        ds1.close()

    ds.close()
    ds = None



ds3 = xr.open_mfdataset(os.path.join(base_path, 'temp', '*.nc'))

ds3.to_netcdf(data_path3)


nc = netCDF4.Dataset(data_path1)
nc.set_auto_mask(False)

# Change staggered variables to unstaggered ones
for vn, v in nc.variables.items():
    if wrftools.Unstaggerer.can_do(v):
        nc.variables[vn] = wrftools.Unstaggerer(v)

# Check if we can add diagnostic variables to the pot
for vn in wrftools.var_classes:
    cl = getattr(wrftools, vn)
    if vn not in nc.variables and cl.can_do(nc):
        nc.variables[vn] = cl(nc)

# trick xarray with our custom netcdf
ds = xr.open_dataset(NetCDF4DataStore(nc))




ds = xr.open_mfdataset(data_path2)



def save1(b):
    """

    """
    c = b.copy()
    c.load().to_netcdf(data_path3)
    c.close()
    c = None

    return ds



ds6 = xr.map_blocks(save1, ds)



block_list = split_grid(ds, x_size=20, y_size=20, n_intervals=None, x_name='lon', y_name='lat', mbytes_size=1500)

s1 = time()
for i, b in enumerate(block_list[:10]):
    print(i)
    c = b.copy()
    c.load().to_netcdf(data_path3)
    c.close()
    c = None

e1 = time()

diff1 = e1 - s1
print(diff1)



# s2 = time()
# with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
#     results = executor.map(save1, block_list[:10])

# e2 = time()

# diff2 = e2 - s2
# print(diff2)

base_path = os.path.split(data_path2)[0]
output_path = os.path.join(base_path, 'temp')

self = Processor()

ds_list = self.load_dataset_metadata(datasets)

# grid1 = self.load_raw_grid(data_path2, lon_dim_name, lat_dim_name, time_dim_name, preprocessor=tu.grid.processors.era5_land.preprocessor)
grid1 = self.load_raw_grid(data_path4, lon_dim_name, lat_dim_name, time_dim_name, preprocessor=preprocessor)

obj_dict = self.determine_grid_block_size(ds_list[0]['dataset_id'])

# self.save_grid_chunks(output_path)

self.save_grid_chunks(output_path, 1)



self = Grid()

ds_list = self.load_dataset_metadata(datasets)

self.load_connection_params(connection_config, bucket, public_url)

run_date='2021-08-29'

self.load_run_date(processing_code, run_date=run_date)

base_path = os.path.split(data_path2)[0]
output_path = os.path.join(base_path, 'temp')
results = os.path.join(output_path, '*.nc')

xy_size = 1
# max_workers = 2
dataset_id=None
sum_closed='right'
other_closed='left'
discrete=False
other_attrs=None
other_encoding=None

self.load_results(results, xy_size, dataset_id, sum_closed, other_closed, discrete, other_attrs, other_encoding)

# self.public_url = public_url

self.update_results(threads=20)

self.update_aggregates()





url1 = 'https://b2.tethys-ts.xyz/file/tethysts/tethys/v2/b2f6bdd8aa592dacb3b257c0/0dce1a2a943fd46e6e7ce6f4/station.json.zst'


resp = requests.get(url1)

s1 = utils.read_json_zstd(resp.content)


















































































