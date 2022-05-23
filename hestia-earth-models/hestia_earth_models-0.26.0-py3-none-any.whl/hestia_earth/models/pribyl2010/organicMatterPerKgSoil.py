from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL
from .utils import new_measurement, _value_func

REQUIREMENTS = {
    "Site": {
        "measurements": {"@type": "Measurement", "term.@id": "organicCarbonPerKgSoil"}
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "min": "",
        "max": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'organicMatterPerKgSoil'
FROM_TERM_ID = 'organicCarbonPerKgSoil'


def _measurement(data: dict):
    measurement = new_measurement(TERM_ID, data)
    measurement['value'] = _value_func(data, lambda v: v * 2)
    measurement['min'] = _value_func(data, lambda v: v * 1.4, 'min')
    measurement['max'] = _value_func(data, lambda v: v * 2.5, 'max')
    return measurement


def _should_run(site: dict):
    measurement = find_term_match(site.get('measurements', []), FROM_TERM_ID)
    has_matter_measurement = len(measurement.get('value', [])) > 0

    logRequirements(model=MODEL, term=TERM_ID,
                    has_matter_measurement=has_matter_measurement)

    should_run = all([has_matter_measurement])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, measurement


def run(site: dict):
    should_run, measurement = _should_run(site)
    return [_measurement(measurement)] if should_run else []
