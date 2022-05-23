import json
from logging import getLogger
import os
from pathlib import Path

import requests

from .GCPGeocodingResults import GCPGeocodingResults

API_KEY_ENV_VAR = 'GCP_GEOCODING_API_KEY'
GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode'
OUTPUT_FORMAT = 'json'
# CACHE_DIR = 'geocoding_cache'
CACHE_DIR = '/tmp/gcp/geocoding/cache'
CACHE_ACCURACY = 5

logger = getLogger(__name__)

def latlng_valid(latitude, longitude):
    try:
        latitude = float(latitude)
    except ValueError:
        logger.error(f"Invalid latitude: {latitude}")
        return None
    try:
        longitude = float(longitude)
    except ValueError:
        logger.error(f"Invalid longitude: {longitude}")
        return None
    if (not isinstance(latitude, float)) or (not isinstance(longitude, float)):
        logger.error(f"Invalid latitude, longitude ({latitude}, {longitude})")
        return None
    if latitude > 90 or latitude < -90:
        logger.error(f"Invalid latitude: {latitude}")
        return None
    if longitude > 180 or longitude < -180:
        logger.error(f"Invalid longitude: {longitude}")
        return None
    return True


def latlng_round(x, cache_accuracy=CACHE_ACCURACY):
    if cache_accuracy == 1:
        return f"{x:.1f}"
    elif cache_accuracy == 2:
        return f"{x:.2f}"
    elif cache_accuracy == 3:
        return f"{x:.3f}"
    elif cache_accuracy == 4:
        return f"{x:.4f}"
    elif cache_accuracy == 5:
        return f"{x:.5f}"
    else:
        return f"{x:.3f}"

def latlng_filepath(latitude, longitude, cache_dir=CACHE_DIR,
                    cache_accuracy=CACHE_ACCURACY):
    lat_str = f"lat{latlng_round(latitude, cache_accuracy)}"
    lng_str = f"lng{latlng_round(longitude, cache_accuracy)}"

    logger.debug(f"{lat_str=}, {lng_str=}")

    lat_dir = f"{cache_dir}/{lat_str}"
    lng_filename = f"{lng_str}.json"

    return lat_dir, lng_filename

def latlng_write_cache(latitude, longitude, results, cache_dir=CACHE_DIR,
                       cache_accuracy=CACHE_ACCURACY, overwrite=False):
    lat_dir, lng_filename = latlng_filepath(latitude, longitude, cache_dir,
                                            cache_accuracy)

    Path(lat_dir).mkdir(parents=True, exist_ok=True)
    lng_file = f"{lat_dir}/{lng_filename}"
    if Path(lng_file).exists() and overwrite == False:
        logger.debug(f"Already in cache {lng_file} and overwrite flag is False")
        return
    with open(lng_file, 'w') as outf:
        json.dump(results, outf)
    outf.close()

def latlng_read_cache(latitude, longitude, cache_dir=CACHE_DIR, cache_accuracy=CACHE_ACCURACY):
    lat_dir, lng_filename = latlng_filepath(latitude, longitude, cache_dir,
                                            cache_accuracy)
    latlng_filename = f"{lat_dir}/{lng_filename}"
    if not Path(latlng_filename).exists():
        logger.debug(f"LatLng Cache miss {latitude=} {longitude=} {cache_dir=} {cache_accuracy=}")
        return None
    with open(latlng_filename) as inf:
        d = json.load(inf)
    inf.close()
    return d

class GCPGeocoding():
    def __init__(self, api_key=None, cache_dir=CACHE_DIR, cache_accuracy=CACHE_ACCURACY):
        if api_key is None:
            self._api_key = os.environ.get(API_KEY_ENV_VAR, None)
            if self._api_key is None:
                logger.critical(f"Cannot determine Geocoding API Key. "
                                f" Set in environment variable {API_KEY_ENV_VAR}")
                return None
        else:
            self._api_key = api_key
        self._cache_dir = cache_dir
        self._cache_accuracy = cache_accuracy

    def reverse(self, latitude, longitude, use_cache=True):
        if not latlng_valid(latitude, longitude):
            return None
        if use_cache:
            cached_results = latlng_read_cache(latitude, longitude, cache_dir=self._cache_dir,
                                               cache_accuracy=self._cache_accuracy)
            if cached_results is not None:
                return GCPGeocodingResults(cached_results)
            else:
                logger.debug(f"Cache miss {latitude=}, {longitude=}")
        url = f"{GEOCODING_URL}/{OUTPUT_FORMAT}"
        params = {}
        params['key'] = self._api_key
        params['latlng'] = f"{latitude},{longitude}"


        r = requests.get(url, params=params)
        if r.status_code != 200:
            logger.error(f"Failed to retrieve address from co-ordinate")
            return None

        d = r.json()
        if d['status'] == 'OK':
            results = GCPGeocodingResults(d['results'])
            latlng_write_cache(latitude, longitude, results.results,
                               cache_dir=self._cache_dir,
                               cache_accuracy=self._cache_accuracy)
            return results

        fake_results = dict()
        fake_results['country'] = None
        fake_results['locality'] = None
        fake_results['neighborhood'] = None

        return fake_results

    def reverse_brief(self, latitude, longitude):
        r = self.reverse(latitude, longitude)
        return r.country, r.locality, r.neighborhood

if __name__ == '__main__':
    pass
