"""
Must be associated with at least 1 `Cycle` that has an
[endDate](https://hestia.earth/schema/Cycle#endDate) after `1958` and before `2021`.
"""
from hestia_earth.schema import MeasurementStatsDefinition
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.cycle import cycle_end_year
from hestia_earth.models.utils.site import related_cycles
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
TERM_ID = 'potentialEvapotranspirationAnnual'
EE_PARAMS = {
    'collection': 'IDAHO_EPSCOR/TERRACLIMATE',
    'ee_type': 'raster_by_period',
    'reducer': 'sum',
    'reducer_regions': 'mean',
    'band_name': 'pet'
}


def _cycle_valid(year: int):
    # NOTE: Currently uses the climate data for the final year of the study
    # see: https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE
    # data is available from 1958-01-01 to 2020-12-01
    return 1958 <= year and year <= 2020


def _measurement(value: float, year: int):
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    measurement['startDate'] = f"{year}-01-01"
    measurement['endDate'] = f"{year}-12-31"
    return measurement


def _download(site: dict, year: int):
    scale = 10
    return download(
        TERM_ID,
        site,
        {
            **EE_PARAMS,
            'year': str(year)
        }
    ).get(EE_PARAMS['reducer_regions'], 0) / scale


def _run(site: dict, year: int):
    value = find_existing_measurement(TERM_ID, site, year) or _download(site, year)
    return _measurement(round(value), year) if value else None


def _should_run(site: dict, year: int):
    geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(site)
    valid_year = _cycle_valid(year)

    logRequirements(model=MODEL, term=TERM_ID,
                    geospatial_data=geospatial_data,
                    max_area_size=MAX_AREA_SIZE,
                    below_max_area_size=below_max_area_size,
                    valid_year=valid_year)

    should_run = all([geospatial_data, below_max_area_size, valid_year])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict):
    cycles = related_cycles(site.get('@id'))
    has_related_cycles = len(cycles) > 0
    years = non_empty_list(set(map(cycle_end_year, cycles)))
    years = list(filter(lambda year: _should_run(site, year), years))
    has_years = len(years) > 0

    logRequirements(model=MODEL, term=TERM_ID,
                    has_related_cycles=has_related_cycles,
                    related_cycles=';'.join(map(lambda c: c.get('@id'), cycles)),
                    has_years=has_years,
                    years=';'.join(map(lambda y: str(y), years)))

    return non_empty_list(map(lambda year: _run(site, year), years))
