import pathlib
from typing import no_type_check

import shapefile  # type: ignore


@no_type_check
def shape_type(code: int) -> str:
    """Look up the name (code) from the integer code reported by shapefile or UNKNOWN"""
    shape_type_map = {
        -1: 'UNKNOWN',
        0: 'NULL',
        1: 'POINT',
        3: 'POLYLINE',
        5: 'POLYGON',
        8: 'MULTIPOINT',
        11: 'POINTZ',
        13: 'POLYLINEZ',
        15: 'POLYGONZ',
        18: 'MULTIPOINTZ',
        21: 'POINTM',
        23: 'POLYLINEM',
        25: 'POLYGONM',
        28: 'MULTIPOINTM',
        31: 'MULTIPATCH',
    }
    name = shape_type_map.get(code)
    return name if name else shape_type_map[-1]


@no_type_check
def load(path: pathlib.Path):
    """Load the shape file at path."""
    with shapefile.Reader(path) as shape:
        shape_type_name = shape_type(shape.shapeType)
        upstream_name = shape.shapeTypeName
        print(f'upstream: {upstream_name} =?= {shape_type_name} :downstream')
        feature_count = len(shape)
        print(f'#features: {feature_count}')
        bounding_box = shape.bbox
        print(f'bbox: {bounding_box}')
        try:
            geo_json = shape.__geo_interface__
            print(f'geojson: {geo_json}')
        except shapefile.ShapefileException as err:
            print(f'problem reading database of shape for {path} with {err}')
        print(shape)
