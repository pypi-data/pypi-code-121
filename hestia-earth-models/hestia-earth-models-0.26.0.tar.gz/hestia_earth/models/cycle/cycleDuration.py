"""
Cycle duration

This model calculates the cycle duration using the cropping intensity for a single year.
"""
from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import valid_site_type
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "365",
        "endDate": "",
        "site": {
            "@type": "Site",
            "siteType": "cropland",
            "measurements": {"@type": "Measurement", "term.@id": "croppingIntensity"}
        }
    }
}
RETURNS = {
    "a `number` or `None` if requirements are not met": ""
}
MODEL_KEY = 'cycleDuration'
DEFAULT_DURATION = 365


def _run(croppingIntensity: float): return croppingIntensity * DEFAULT_DURATION


def _should_run(cycle: dict):
    site = cycle.get('site', {})
    end_date = cycle.get('endDate')
    croppingIntensity = most_relevant_measurement_value(site.get('measurements', []), 'croppingIntensity', end_date)
    cycleDuration = cycle.get('cycleDuration')
    site_type_valid = valid_site_type(cycle)

    logRequirements(model=MODEL, key=MODEL_KEY,
                    cycleDuration=cycleDuration,
                    croppingIntensity=croppingIntensity,
                    site_type_valid=site_type_valid)

    should_run = all([site_type_valid, cycleDuration == 365, croppingIntensity])
    logShouldRun(MODEL, None, should_run, key=MODEL_KEY)
    return should_run, croppingIntensity


def run(cycle: dict):
    should_run, croppingIntensity = _should_run(cycle)
    return _run(croppingIntensity) if should_run else None
