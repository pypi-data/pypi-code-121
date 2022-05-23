from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from .utils import get_liquid_slurry_sludge_P_total
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "inputs": [{"@type": "Input", "term.termType": "organicFertilizer"}],
        "site": {
            "@type": "Site",
            "country": "",
            "measurements": [
                {"@type": "Measurement", "term.@id": "drainageClass"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "organicFertilizer": "OrganicFertilizerClassification"
}
TERM_ID = 'pToDrainageWaterSoilFlux'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, drainageClass: list):
    P_total, _ = get_liquid_slurry_sludge_P_total(cycle)
    value = 0.07 * (1 + P_total * 0.2/80) * (6 if drainageClass > 3 else 0)
    return [_emission(value)]


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    drainageClass = most_relevant_measurement_value(measurements, 'drainageClass', end_date)

    logRequirements(model=MODEL, term=TERM_ID,
                    drainageClass=drainageClass)

    should_run = all([drainageClass])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, drainageClass


def run(cycle: dict):
    should_run, drainageClass = _should_run(cycle)
    return _run(cycle, drainageClass) if should_run else []
