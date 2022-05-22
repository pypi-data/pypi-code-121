import shapely.geometry as geo
import numpy as np
import json


class GeoJSON:
    def __init__(self):
        self._json = self._create_base_geojson()

    def _create_base_geojson(self) -> dict:
        return {
            'type': 'FeatureCollection',
            'features': []
        }

    def _create_base_object(self) -> dict:
        return {
            'type': 'Feature',
            'properties': {},
            'geometry': {}
        }

    def _check_object_type(self, object, expected_type: str) -> bool:
        if object.geom_type == expected_type:
            return True
        else:
            return False

    def write_to_file(self, file_path: str) -> None:
        with open(file=file_path, mode='w') as json_file:
            json.dump(self._json, json_file, indent=2)

    def add_point(self, point: geo.Point) -> None:
        """Adds point to object.
        If provided point of wrong type raises TypeError"""
        if not self._check_object_type(point, 'Point'):
            raise TypeError('Provided polygon not of shapely.geometry.Point type.')

        new_obj = self._create_base_object()
        geometry = new_obj['geometry']
        geometry['type'] = 'Point'
        geometry['coordinates'] = np.asarray(point.coords).tolist()[0]

        self._json['features'].append(new_obj)

    def add_polygon(self, polygon: geo.Polygon) -> None:
        """Adds polygon to object.
        If provided polygon of wrong type raises TypeError"""
        if not self._check_object_type(polygon, 'Polygon'):
            raise TypeError('Provided polygon not of shapely.geometry.polygon.Polygon type.')

        new_obj = self._create_base_object()
        geometry = new_obj['geometry']
        geometry['type'] = 'Polygon'
        geometry['coordinates'] = [np.array(polygon.exterior.coords).tolist()]

        self._json['features'].append(new_obj)

    def add_linestring(self, line_string: geo.LineString) -> None:
        """Adds LineString to object.
        If provided LineString of wrong type raises TypeError"""
        if not self._check_object_type(line_string, 'LineString'):
            raise TypeError('Provided polygon not of shapely.geometry.LineString type.')

        new_obj = self._create_base_object()
        geometry = new_obj['geometry']
        geometry['type'] = 'LineString'
        geometry['coordinates'] = np.array(line_string.coords).tolist()

        self._json['features'].append(new_obj)
