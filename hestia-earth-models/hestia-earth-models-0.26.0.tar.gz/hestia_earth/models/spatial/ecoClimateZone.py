"""
They approximataely map to the [IPCC (2019) Climate Zones](https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch03_Land%20Representation.pdf).  # noqa: E501
Data are derived from [Hiederer et al. (2010) Biofuels: A new methodology to estimate GHG emissions from global land use change, European Commission Joint Research Centre](https://ec.europa.eu/jrc/en/publication/eur-scientific-and-technical-research-reports/biofuels-new-methodology-estimate-ghg-emissions-due-global-land-use-change-methodology).  # noqa: E501

| Value | Climate Zone         |
|-------|----------------------|
| 1     | Warm Temperate Moist |
| 2     | Warm Temperate Dry   |
| 3     | Cool Temperate Moist |
| 4     | Cool Temperate Dry   |
| 5     | Polar Moist          |
| 6     | Polar Dry            |
| 7     | Boreal Moist         |
| 8     | Boreal Dry           |
| 9     | Tropical Montane     |
| 10    | Tropical Wet         |
| 11    | Tropical Moist       |
| 12    | Tropical Dry         |
"""
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
TERM_ID = 'ecoClimateZone'
EE_PARAMS = {
    'collection': 'climate_zone',
    'ee_type': 'raster',
    'reducer': 'mode',
    'fields': 'mode'
}
BIBLIO_TITLE = 'Hiederer et al. 2010, Biofuels: A new methodology to estimate GHG emissions from global land use change'


def _measurement(value: int):
    measurement = _new_measurement(TERM_ID, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict):
    return download(TERM_ID, site, EE_PARAMS).get(EE_PARAMS['reducer'])


def _run(site: dict):
    value = find_existing_measurement(TERM_ID, site) or _download(site)
    return [_measurement(round(value))] if value else []


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
