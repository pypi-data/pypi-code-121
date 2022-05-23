import os
from hestia_earth.schema import SchemaType
from hestia_earth.utils.tools import current_time_ms
from hestia_earth.utils.api import search
from hestia_earth.earth_engine import run, should_run

from hestia_earth.models.log import debugValues, logger, logErrorRun
from hestia_earth.models.utils import is_from_model, _load_calculated_node
from . import MODEL

EXISTING_SEARCH_ENABLED = os.getenv('ENABLE_EXISTING_SEARCH', 'false').lower() == 'true'
MAX_AREA_SIZE = int(os.getenv('MAX_AREA_SIZE', '5000'))


def _collection_name(id: str): return id if '/' in id else f"users/hestiaplatform/{id}"


def _has_coordinates(site: dict): return site.get('latitude') is not None and site.get('longitude') is not None


def _site_gadm_id(site: dict): return site.get('region', site.get('country', {})).get('@id')


def has_geospatial_data(site: dict, by_region=True):
    """
    Determines whether the Site has enough geospatial data to run calculations. We are checking for:
    1. If the coordinates (latitude and longitude) are present
    2. Otherwise if the `region` or `country` is present
    3. Otherwise if the `boundary` is present
    Note: this is a general pre-check only, each model can have 1 or more other checks.

    Parameters
    ----------
    site : dict
        The `Site` node.
    by_region : bool
        If we can run using the region ID (`region` or `country` fields). Defaults to true.

    Returns
    -------
    bool
        If we should run geospatial calculations on this model or not.
    """
    has_region = _site_gadm_id(site) is not None
    has_boundary = site.get('boundary') is not None
    return _has_coordinates(site) or (by_region and has_region) or has_boundary


def _geospatial_data(site: dict, by_region=True):
    return {
        'latitude': site.get('latitude'),
        'longitude': site.get('longitude'),
        'boundary': site.get('boundary'),
        **({'gadm_id': _site_gadm_id(site)} if by_region else {})
    }


def should_download(site: dict, by_region=True) -> bool:
    try:
        return should_run(_geospatial_data(site, by_region))
    except Exception as e:
        # if the type is unknown, a geospatial param is missing and will be detected by `has_geospatial_data`
        return 'Unkown type' in str(e)


def download(term: str, site: dict, data: dict, by_region=True) -> dict:
    """
    Downloads data from Hestia Earth Engine API.

    Returns
    -------
    dict
        Data returned from the API.
    """
    now = current_time_ms()
    try:
        collection = data.get('collection')
        res = run({
            **data,
            **_geospatial_data(site, by_region=by_region),
            'max_area': MAX_AREA_SIZE,
            'collection': _collection_name(collection)
        })
        properties = res.get('features', [{'properties': {}}])[0].get('properties')
        debugValues(collection=collection, time=f"{current_time_ms() - now}ms", properties=properties)
        return properties
    except Exception as e:
        logErrorRun(MODEL, term, str(e))
        return {}


def _coordinates_query(site: dict):
    return {
        'filter': {
            'geo_distance': {
                'distance': '1m',
                'location': {
                    'lat': site.get('latitude'),
                    'lon': site.get('longitude')
                }
            }
        }
    } if _has_coordinates(site) else None


def _region_query(site: dict):
    query = [
        {'match': {'region.name.keyword': site.get('region').get('name')}}
    ] if site.get('region') else [
        {'match': {'country.name.keyword': site.get('country').get('name')}}
    ] if site.get('country') else None
    return {
        'should': query,
        'minimum_should_match': 1
    } if query else None


def _find_measurement(site: dict, term_id, year: int = None):
    def match(measurement: dict):
        # only use measurements that have been added by the spatial models
        is_added = is_from_model(measurement) and measurement.get('methodModel', {}).get('@id') == MODEL
        # match year if required
        same_year = year is None or measurement.get('endDate').startswith(str(year))
        return is_added and same_year and measurement.get('term', {}).get('@id') == term_id

    return next((m for m in site.get('measurements', []) if match(m)), None)


def _find_existing_sites(site: dict):
    location_query = _coordinates_query(site) or _region_query(site)
    query = {
        'bool': {
            'must': [
                {'match': {'@type': SchemaType.SITE.value}}
            ],
            **location_query
        }
    } if location_query else None
    return search(query, sort={'createdAt': 'asc'}) if EXISTING_SEARCH_ENABLED and query else []


def find_existing_measurement(term_id: str, site: dict, year: int = None):
    """
    Find the same Measurement in existing Site to avoid calling the Hestia Earth Engine API.

    Returns
    -------
    dict
        Measurement if found.
    """
    sites = _find_existing_sites(site)
    for site in sites:
        data = _load_calculated_node(site, SchemaType.SITE)
        measurement = _find_measurement(data, term_id, year)
        if measurement:
            value = measurement.get('value', [None])[0]
            logger.debug('model=%s, term=%s, matching measurement value=%s', MODEL, term_id, value)
            return value
    return None
