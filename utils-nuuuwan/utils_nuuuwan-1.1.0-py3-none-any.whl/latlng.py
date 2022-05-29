import math

from utils import geo

PRECISION = 6
ABS_TOL = 0.1 ** PRECISION


class Bounds:
    def __init__(self, min_latlng, max_latlng):
        self.min_latlng = min_latlng
        self.max_latlng = max_latlng

    @property
    def min_lat(self):
        return self.min_latlng.lat

    @property
    def min_lng(self):
        return self.min_latlng.lng

    @property
    def max_lat(self):
        return self.max_latlng.lat

    @property
    def max_lng(self):
        return self.max_latlng.lng

    def __add__(self, other):
        return Bounds(
            LatLng(
                min(self.min_lat, other.min_lat),
                min(self.min_lng, other.min_lng),
            ),
            LatLng(
                max(self.max_lat, other.max_lat),
                max(self.max_lng, other.max_lng),
            ),
        )

    @property
    def span(self):
        return [self.max_lat - self.min_lat, self.max_lng - self.min_lng]

    def __eq__(self, other):
        return all([
            self.min_latlng == other.min_latlng,
            self.max_latlng == other.max_latlng,
        ])

    def __str__(self):
        return str([self.min_latlng, self.max_latlng])


class LatLng:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def __str__(self):
        return f'({self.lat:.6f}, {self.lng:.6f})'

    def __eq__(self, other):
        return all([math.isclose(self.lat, other.lat, abs_tol=ABS_TOL),
                   math.isclose(self.lng, other.lng, abs_tol=ABS_TOL), ])

    @property
    def raw(self):
        return [self.lat, self.lng]

    @property
    def bounds(self):
        return Bounds(self, self)

    def distance(self, other):
        return geo.get_distance(self.raw, other.raw)


class LatLngIndex:
    POINT_PEDRO = LatLng(9.835556, 80.212222)
    DONDRA_HEAD = LatLng(5.923389, 80.589694)
    SANGAMAN_KANDA = LatLng(7.022222, 81.879167)
    KANCHCHATHEEVU = LatLng(9.383333, 79.516667)


class Polygon:
    def __init__(self, latlng_list):
        self.latlng_list = latlng_list

    def __iter__(self):
        for latlng in self.latlng_list:
            yield latlng

    def __len__(self):
        return len(self.latlng_list)

    @property
    def bounds(self):
        bounds = None
        for latlng in self:
            if not bounds:
                bounds = latlng.bounds
            else:
                bounds = bounds + latlng.bounds
        return bounds
