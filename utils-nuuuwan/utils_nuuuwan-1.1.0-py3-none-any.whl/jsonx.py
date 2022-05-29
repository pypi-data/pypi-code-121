"""JSON utils."""
import base64
import json

from geopandas.geodataframe import GeoDataFrame
from pandas import read_pickle
from pandas.core.frame import DataFrame
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry

from utils import filex


def read(file_name):
    """Read JSON from file.

    Args:
        file_name (str): file name

    Returns:
        Parsed JSON data

    """
    return json.loads(filex.read(file_name))


def write(file_name, data):
    """Write data as JSON to file.

    Args:
        file_name (str): file name
        data: data as serializable object

    """
    filex.write(file_name, json.dumps(data, indent=2))


def serialize(data):
    if isinstance(data, bytes):
        return {
            'type': 'bytes',
            'data': base64.b64encode(data).decode('ascii'),
        }
    if isinstance(data, BaseGeometry):
        return {
            'type': 'BaseGeometry',
            'data': mapping(data),
        }

    if isinstance(data, GeoDataFrame):
        tmp_file = filex.get_tmp_file()
        return {
            'type': 'GeoDataFrame',
            'data': data.to_pickle(tmp_file),
            'pickle_file': tmp_file,
        }
    if isinstance(data, DataFrame):
        tmp_file = filex.get_tmp_file()
        return {
            'type': 'DataFrame',
            'data': data.to_pickle(tmp_file),
            'pickle_file': tmp_file,
        }

    return {
        'type': None,
        'data': data,
    }


def deserialize(data):
    data_type = data['type']
    data_data = data['data']

    if data_type == 'bytes':
        return base64.b64decode(data_data)
    if data_type == 'BaseGeometry':
        return shape(data_data)

    if data_type == 'GeoDataFrame':
        pickle_file = data['pickle_file']
        return read_pickle(pickle_file)
    if data_type == 'DataFrame':
        pickle_file = data['pickle_file']
        return read_pickle(pickle_file)

    return data_data
