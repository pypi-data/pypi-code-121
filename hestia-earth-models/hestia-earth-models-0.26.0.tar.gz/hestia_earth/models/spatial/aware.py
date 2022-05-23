"""
Aware Water Basin ID

This model calculates the the [AWARE](https://wulca-waterlca.org/) water basin identifier.
"""
from hestia_earth.models.log import logRequirements, logShouldRun
from .utils import MAX_AREA_SIZE, download, has_geospatial_data, should_download
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": ""}
        ]
    }
}
RETURNS = {
    "The AWARE water basin identifier as a `string`": ""
}
KEY = 'aware'
EE_PARAMS = {
    'collection': 'AWARE',
    'ee_type': 'vector',
    'field': 'Name'
}


def _download(site: dict):
    return download(KEY, site, EE_PARAMS, by_region=False).get(EE_PARAMS['field'])


def _run(site: dict): return _download(site)


def _should_run(site: dict):
    geospatial_data = has_geospatial_data(site, by_region=False)
    below_max_area_size = should_download(site, by_region=False)

    logRequirements(model=MODEL, key=KEY,
                    geospatial_data=geospatial_data,
                    max_area_size=MAX_AREA_SIZE,
                    below_max_area_size=below_max_area_size)

    should_run = all([geospatial_data, below_max_area_size])
    logShouldRun(MODEL, None, should_run, key=KEY)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
