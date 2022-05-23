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
        "startDate": "",
        "endDate": "",
        "statsDefinition": "spatial"
    }]
}
TERM_ID = 'potentialEvapotranspirationLongTermAnnualMean'
START_DATE = '1979-01-01'
END_DATE = '2020-12-31'
EE_PARAMS = {
    'collection': 'IDAHO_EPSCOR/TERRACLIMATE',
    'ee_type': 'raster_by_period',
    'reducer': 'sum',
    'reducer_regions': 'mean',
    'reducer_years': 'mean',
    'band_name': 'pet',
    'start_date': START_DATE,
    'end_date': END_DATE
}


def _measurement(value: float):
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    measurement['startDate'] = START_DATE
    measurement['endDate'] = END_DATE
    return measurement


def _download(site: dict):
    scale = 10
    return download(TERM_ID, site, EE_PARAMS).get(EE_PARAMS['reducer_years'], 0) / scale


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
