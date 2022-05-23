"""
Ecoregion

Ecoregions represent the original distribution of distinct assemblages of species and communities.
There are 867 terrestrial ecoregions as
[defined by WWF](https://www.worldwildlife.org/publications/terrestrial-ecoregions-of-the-world).
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
    "The WWF Terrestrial Ecoregion name as a `string`": ""
}
KEY = 'ecoregion'
EE_PARAMS = {
    'collection': 'Terrestrial_Ecoregions_World',
    'ee_type': 'vector',
    'fields': 'eco_code'
}


def _download(site: dict):
    return download(KEY, site, EE_PARAMS, by_region=False).get(EE_PARAMS['fields'])


def _run(site: dict):
    try:
        value = _download(site)
    except Exception:
        value = None
    return value


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
