from hestia_earth.schema import MeasurementStatsDefinition, SiteSiteType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.site import valid_site_type
from .utils import MAX_AREA_SIZE, download, find_existing_measurement, has_geospatial_data, should_download
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
    "Measurement": [{
        "value": "",
        "statsDefinition": "spatial"
    }]
}
TERM_ID = 'waterDepth'
EE_PARAMS = {
    'collection': 'gebco_2021_tid',
    'ee_type': 'raster',
    'reducer': 'mean',
    'fields': 'mean'
}


def _measurement(value: float):
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict):
    return download(TERM_ID, site, EE_PARAMS, by_region=False).get(EE_PARAMS['reducer'])


def _run(site: dict):
    value = find_existing_measurement(TERM_ID, site) or _download(site)
    return [_measurement(value)] if value is not None else []


def _should_run(site: dict):
    geospatial_data = has_geospatial_data(site, by_region=False)
    below_max_area_size = should_download(site, by_region=False)
    site_type_valid = valid_site_type(site, [SiteSiteType.SEA_OR_OCEAN.value])

    logRequirements(model=MODEL, term=TERM_ID,
                    geospatial_data=geospatial_data,
                    max_area_size=MAX_AREA_SIZE,
                    below_max_area_size=below_max_area_size,
                    site_type_valid=site_type_valid)

    should_run = all([geospatial_data, below_max_area_size, site_type_valid])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
