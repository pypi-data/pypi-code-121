"""
Soil Amendments

This model checks if the `soilPh` from geospatial dataset is greater than `6.5` and updates the
[Data Completeness](https://hestia.earth/schema/Completeness#soilAmendments) value.
"""
from hestia_earth.models.log import logger
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.measurement import most_relevant_measurement, measurement_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.soilAmendments": "False",
        "endDate": "",
        "site": {
            "@type": "Site",
            "measurements": {"@type": "Measurement", "term.@id": "soilPh"}
        }
    }
}
RETURNS = {
    "Completeness": {
        "soilAmendments": ""
    }
}
MODEL_KEY = 'soilAmendments'


def run(cycle: dict):
    end_date = cycle.get('endDate')
    measurements = cycle.get('site', {}).get('measurements', [])
    soilPh_measurement = most_relevant_measurement(measurements, 'soilPh', end_date)
    soilPh = measurement_value(soilPh_measurement)
    is_complete = is_from_model(soilPh_measurement) and soilPh > 6.5
    logger.debug('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
