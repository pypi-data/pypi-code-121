#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  7 09:29:29 2021

@author: mike
"""
import numpy as np
import xarray as xr
import pandas as pd
import os
import glob
# from tethys_utils.processing import write_pkl_zstd, process_datasets, prepare_results, assign_station_id, make_run_date_key
# from tethys_utils.s3 import process_run_date, update_results_s3, put_remote_dataset, put_remote_agg_stations, put_remote_agg_datasets, s3_connection
from tethys_utils import misc, s3, processing, titan, data_io, grid
from shapely.geometry import shape, mapping, Point, box
import copy
import rasterio
import concurrent.futures
import rioxarray as rxr


###########################################
### Parameters


############################################
### Functions


def parse_images(glob_str):
    """

    """
    if isinstance(glob_str, str):
        f2 = glob.glob(glob_str)
    elif isinstance(glob_str, list):
        f2 = glob_str.copy()
    else:
        raise TypeError

    f3 = {f: os.path.getsize(f) for f in f2}
    max1 = max(f3.values())
    max_f = [f for f in f3 if f3[f] == max1][0]

    return f3, max_f


# def process_image(image, parameter, time, height, x_name='x', y_name='y', band=1):
#     """

#     """
#     time1 = pd.Timestamp(time)

#     xr1 = rxr.open_rasterio(image)
#     xr1 = xr1.rename({x_name: 'lon', y_name: 'lat'}).sel(band=band).drop('band')
#     xr1 = xr1.assign_coords(height=height).expand_dims('height', axis=2)
#     xr1 = xr1.assign_coords(time=time1).expand_dims('time')
#     xr1.name = parameter

#     return xr1


def prepare_raster(image, parameter, x_name='x', y_name='y', band=1):
    """

    """
    xr1 = rxr.open_rasterio(image)
    xr1 = xr1.rename({x_name: 'lon', y_name: 'lat'}).sel(band=band).drop('band')
    xr1.name = parameter

    return xr1


############################################
### Class


class Raster(grid.Grid):
    """

    """
    ## Initial import and assignment function
    def import_raster(self, source_paths, time, height, x_name='x', y_name='y', band=1):
        """

        """
        misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

        f_dict, max_f = parse_images(source_paths)

        ## Run checks
        src = rasterio.open(max_f)
        crs = src.crs

        if crs.to_epsg() != 4326:
            raise ValueError('Raster CRS is in epsg: ' + str(crs) + ', but should be 4326')

        src.close()

        # Set attrs
        raster_attrs = {'time': time, 'band': band, 'height': height, 'images': f_dict, 'max_image': max_f, 'x_name': x_name, 'y_name': y_name, 'crs': crs}

        setattr(self, 'raster_attrs', raster_attrs)

        return crs.to_proj4()


    def spatial_merge_rasters(self, remove_source_images=False):
        """

        """
        raster_attrs = self.raster_attrs.copy()

        ## Merge images
        time1 = pd.Timestamp(raster_attrs['time']).round('S')
        time_str = time1.strftime('%Y%m%d%H%M%S')
        dataset = self.dataset_list[0]
        parameter = dataset['parameter']
        ds_id = dataset['dataset_id']

        merged_raster = os.path.join(self.preprocessed_path, '{ds_id}--{param}--{height}--{time}.tif'.format(param=parameter, time=time_str, ds_id=ds_id, height=raster_attrs['height']))

        f_dict = raster_attrs['images']
        source_paths = list(f_dict.keys())

        if len(source_paths) > 0:
            data_io.gdal_merge(source_paths, merged_raster)
        else:
            _ = data_io.copy_file(source_paths[0], merged_raster)

        if remove_source_images:
            for i in source_paths:
                os.remove(i)

        return merged_raster


    # def open_big_one(self):
    #     """

    #     """
    #     xr1 = xr.open_rasterio(self.max_image)

    #     return xr1


    # def determine_grid_block_size(self, starting_x_size=100, starting_y_size=100, increment=100, min_size=800, max_size=1100):
    #     """

    #     """
    #     parameter = self.grid.datasets[0]['parameter']
    #     xr1 = process_image(self.max_image, parameter, x_name=self.x_name, y_name=self.y_name, band=1)
    #     self.grid.load_data(xr1.to_dataset(), parameter, self.time, self.height)
    #     size_dict = self.grid.determine_grid_block_size(starting_x_size, starting_y_size, increment, min_size, max_size)

    #     setattr(self, 'grid_size_dict', size_dict)

    #     res = xr1.attrs['res'][0]
    #     setattr(self, 'grid_res', res)

    #     return size_dict


    # def save_results(self, x_size, y_size, threads=30):
    #     """

    #     """
    #     ## Iterate through the images
    #     images = list(self.images.keys())
    #     images.sort()

    #     for tif in images:
    #         print(tif)

    #         parameter = self.grid.datasets[0]['parameter']
    #         xr1 = process_image(self.max_image, parameter, x_name=self.x_name, y_name=self.y_name, band=1)
    #         self.grid.load_data(xr1.to_dataset(), parameter, self.time, self.height)

    #         self.grid.save_results(x_size, y_size, threads=threads)










