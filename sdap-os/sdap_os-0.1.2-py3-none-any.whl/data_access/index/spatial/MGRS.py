import mgrs
import utm
import numpy as np
import math
import string


class MGRS:

    def __init__(self, level=5):
        # level 5 is tiles of 100 km square side
        # ...
        # level 1 is tile of 1 m square side
        self.level = level
        self.tile_side = 1*10**self.level
        self.m = mgrs.MGRS()

    def _truncate(self, code):
        # '18TYM0013086273'
        prefix = code[:5]
        easting = code[5:10]
        northing = code[10:]

        return prefix + easting[:5-self.level] + northing[:5-self.level]

    @staticmethod
    def _get_utm_zone(lat, lon):

        zone_x = math.floor((lon + 180) / 6)
        zone_y_ref = list(string.ascii_uppercase)[2:-2]
        zone_y_ref.remove('I')
        zone_y_ref.remove('O')
        zone_y = zone_y_ref[math.floor((lat + 80) / 8)]

        return zone_x, zone_y

    @staticmethod
    def _remove_offset_in_mgrs(code):
        zone_x_no_offset = "{:02d}".format(int(code[0:1]) - 1)
        return zone_x_no_offset + code[2:]


    def get_codes(self, lon_range, lat_range):

        key_lons = np.arange(lon_range[0], lon_range[1], 6)
        key_lons = np.append(key_lons, lon_range[1])
        key_lats = np.arange(lat_range[0], lat_range[1], 8)
        key_lats = np.append(key_lats, lat_range[1])

        mgrs_codes = []
        for i in range(len(key_lats)-1):
            for j in range(len(key_lons)-1):

                ll_x, ll_y, utm_zone_x, utm_zone_y = utm.from_latlon(key_lats[j], key_lons[i])
                ur_x, ur_y, _, _ = utm.from_latlon(key_lats[j+1], key_lons[i+1], utm_zone_x, utm_zone_y)
                key_xs = np.arange(ll_x, ur_x, self.tile_side)
                key_ys = np.arange(ll_y, ur_y, self.tile_side)
                for key_x in key_xs:
                    for key_y in key_ys:
                        latlon = utm.to_latlon(key_x, key_y, utm_zone_x, utm_zone_y)
                        mgrs_codes.append(self._truncate(self.m.toMGRS(*latlon)))
                # for a weird reason there is a negative offset for HLS data naming, in longitude
                mgrs_codes = [MGRS._remove_offset_in_mgrs(code) for code in mgrs_codes]

        #return mgrs_codes
        return ['18TYN']

