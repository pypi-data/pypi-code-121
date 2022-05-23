from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import MAX_AREA_SIZE, download, find_existing_measurement, has_geospatial_data, should_download
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": ""},
            {"region": ""}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "statsDefinition": "spatial"
    }]
}
TERM_ID = 'nutrientLossToAquaticEnvironment'
EE_PARAMS = {
    'collection': 'r_fraction_loss_water',
    'ee_type': 'raster',
    'reducer': 'mean',
    'fields': 'mean'
}
BIBLIO_TITLE = 'Modelling spatially explicit impacts from phosphorus emissions in agriculture'


def _measurement(value: float):
    measurement = _new_measurement(TERM_ID, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict):
    return download(TERM_ID, site, EE_PARAMS).get(EE_PARAMS['reducer'], 0) * 100


def _run(site: dict):
    value = find_existing_measurement(TERM_ID, site) or _download(site)
    return [_measurement(value)] if value is not None else []


def _should_run(site: dict):
    geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(site)

    logRequirements(model=MODEL, term=TERM_ID,
                    geospatial_data=geospatial_data,
                    max_area_size=MAX_AREA_SIZE,
                    below_max_area_size=below_max_area_size)

    should_run = all([geospatial_data, below_max_area_size])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
