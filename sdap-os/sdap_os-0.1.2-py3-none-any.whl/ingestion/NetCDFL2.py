import xarray
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from functools import partial

from sdap.utils import get_log

logger = get_log(__name__)


class NetCDFL2:

    def __init__(self, file_path, spatial_index, temporal_index, group=None):
        self._file_path = file_path
        self._group = group
        self._spatial_index = spatial_index
        self._temporal_index = temporal_index

    @staticmethod
    def get_code(time, lat, lon, spatial_index, temporal_index):
        current_datetime = datetime.fromisoformat(time.replace('Z', '+00:00'))
        temporal_key = temporal_index.get_code(current_datetime)
        spatial_key = spatial_index.get_code(lat, lon, crs='epsg:4326')
        return spatial_key + temporal_key



    def get_tiles(self):
        if self._group:
            dataset = xarray.open_dataset(self._file_path, group=self._group)
        else:
            dataset = xarray.open_dataset(self._file_path)

        obs_date = dataset.time_utc.astype(np.datetime64)
        obs_date = self._temporal_index.get_xa_codes(obs_date)

        lon_lat = xarray.concat([dataset.longitude, dataset.latitude], dim='spatial_coord')
        lon_lat = lon_lat.transpose('time', 'scanline', 'ground_pixel', 'spatial_coord')
        a = xarray.apply_ufunc(self._spatial_index.get_matrix_codes,
                           lon_lat,
                           input_core_dims=[['spatial_coord']])

        t_dim = len(dataset.time)
        x_dim = len(dataset.scanline)
        y_dim = len(dataset.ground_pixel)
        s2_codes = np.empty((t_dim,x_dim, y_dim), dtype=object)
        s2_unique_codes = set()
        for t in range(t_dim):
            for i in range(x_dim):
                current_datetime = datetime.fromisoformat(dataset.time_utc.data.item(t, i).replace('Z', '+00:00'))
                temporal_key = self._temporal_index.get_code(current_datetime)
                for j in range(y_dim):
                    lat = dataset.latitude.data.item(t, i, j)
                    lon = dataset.longitude.data.item(t, i, j)
                    spatial_key = self._spatial_index.get_code(lat, lon, crs='epsg:4326')
                    current_code = spatial_key + temporal_key
                    logger.debug("key found %s", current_code)
                    s2_codes[t][i][j] = current_code
                    s2_unique_codes.add(current_code)

        dataset = dataset.assign({'s2_codes': (('time', 'x', 'y'), s2_codes)})

        fig = plt.figure()
        ax = plt.axes(projection=ccrs.PlateCarree())

        # background
        ax.add_wmts('https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi',
                    'ASTER_GDEM_Greyscale_Shaded_Relief')

        # extent
        #ax.set_extent([dataset.longitude.min(), dataset.longitude.max(), dataset.latitude.min(), dataset.latitude.max()], crs=ccrs.PlateCarree())

        dataset = dataset.isel(time=0)
        color_map = ax.pcolormesh(dataset.longitude, dataset.longitude, dataset.variables['s2_codes'], alpha=0.5, transform=ccrs.PlateCarree())
        fig.colorbar(color_map, ax=ax)
        plt.show()
