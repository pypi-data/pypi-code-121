#!/usr/bin/env python3

from typing import List
import xarray as xr
from pathlib import Path
import zarr
import sys

import climetlab as cml
import climetlab_cems_flood as cmf

"""
1. read grib (small/big/multifiles)
2. chunk/rechunk
3. write to zarr

"""

def read_grib(path: Path,fnames: List[str]) -> xr.Dataset:
    paths = [ path / f for f in fnames]
    ds = xr.open_mfdataset(paths, engine = "cfgrib",combine='nested',concat_dim='time')
    return ds
    
nwse = [50.972204,5.450796, 46.296530, 11.871059] # Ryne

big = lambda: cml.load_dataset(
            'cems-flood-glofas-forecast',
            model='lisflood',
            product_type='ensemble_perturbed_forecasts',
            system_version='operational',
            period= '20210710-20210711',#'2001-200401-04*',
            leadtime_hour = '24-120',
            variable="river_discharge_in_the_last_24_hours",
            #area= nwse,
            split_on = ['day'],
            threads = 6,
            merger=None
        )
small = lambda: cml.load_dataset(
            'cems-flood-glofas-forecast',
            model='lisflood',
            product_type='ensemble_perturbed_forecasts',
            system_version='operational',
            period= '20210710-20210711',#'2001-200401-04*',
            leadtime_hour = '24-120',
            variable="river_discharge_in_the_last_24_hours",
            area= nwse,
            split_on = ['day'],
            threads = 6,
            merger=None
        )
# fnames_big = ['c-dsretriever-014f6a32e31dd06cb87cbcefc56ed05f51fdfb7c7bd77872ab9492c7ad4d3335.grib','c-dsretriever-198eaf5c4c49bb05340ef9057d036abea56e5152bbd8b413fc4fc5cf57934bea.grib'] # 1.3G
# fnames_small = ['c-dsretriever-88d434ccc1f427d0223ac2f284c5862666305c43a907231ae963316635962415.grib','c-dsretriever-94f19111e77462d6d04ca9b8f1e156924bc2eff484c9fd0de629c1a2ec8232aa.grib']

ALL = {"small": small,
         "big": big }

if __name__ == '__main__':
    
    typ = sys.argv[1]
    print(typ)
    # path = Path('/tmp/climetlab-iacopo')
    # ds = read_grib(path, ALL.get(typ))
    # ds = ds.chunk({'number':1,'latitude':20,'longitude':20})
    
    ds = ALL.get(typ)().to_xarray()
    
    ds = ds.chunk({"realization":1,
                      "forecast_reference_time": 1,
                      "leadtime": -1,
                      "lat": 250,
                      "lon": 250})
    
    ds.to_zarr(f"/data/temp/test_{typ}.zarr",mode="w")