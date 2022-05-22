import logging
import fsspec
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from pyproj import Transformer
import s2sphere
import time

logging.getLogger('fiona').setLevel(logging.WARNING)

class S2Key:
    def __init__(self, id):
        binary_id = bin(id)[2:] # remove 0b
        self.face = binary_id[:3]
        last_one_index = binary_id.rfind('1')
        self.hilbert_number = binary_id[3:last_one_index]

    def get_id(self, level=30):
        binary_id_without_trailing_zeros = self.face + self.hilbert_number[:2*level] + '1'
        binary_id = f'{binary_id_without_trailing_zeros:<064}'
        return int(binary_id, 2)


class GoogleS2:

    def __init__(self, level=30):
        self._level = level

        self._coverer = s2sphere.RegionCoverer()
        self._coverer.min_level = level
        self._coverer.max_level = level
        self._coverer.max_cells = 1

    def get_code(self, x, y, crs='epsg:4326'):
        start = time.time()

        coord_transformer = Transformer.from_crs(crs, "epsg:4326")
        coords = coord_transformer.transform(x, y)

        point = s2sphere.LatLng.from_degrees(coords[0], coords[1]).to_point()
        region = s2sphere.Cap.from_axis_height(point, 0)
        code = str(self._coverer.get_covering(region)[0].id())

        end = time.time()
        #print(end - start)

        return code



    def get_list_coord_code(self, list_coords, crs='epsg:4326'):
        [x, y] = list_coords
        return self.get_code(x, y, crs=crs)

    def get_matrix_codes(self, matrix_coords, crs='epsg:4326'):

        def _get_code(coords):
            return self.get_code(*coords, crs=crs)

        return np.apply_along_axis(_get_code, 3, matrix_coords)

    def get_codes(self, x_range, y_range, crs):
        pass
