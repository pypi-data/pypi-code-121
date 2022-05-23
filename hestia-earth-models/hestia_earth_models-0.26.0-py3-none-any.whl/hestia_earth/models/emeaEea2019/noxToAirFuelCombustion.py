from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from .utils import _get_fuel_values
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "inputs": [
                {"@type": "Input", "term.termType": "fuel"}
            ],
            "dataCompleteness.electricityFuel": "True"
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
TERM_ID = 'noxToAirFuelCombustion'
TIER = EmissionMethodTier.TIER_1.value
DIESEL_COMB_NOX = 0.032629
GASOLINE_COMB_NOX = 0.007117


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(diesel_values: list, gasoline_values: list):
    diesel_value = list_sum(diesel_values) * DIESEL_COMB_NOX
    gasoline_value = list_sum(gasoline_values) * GASOLINE_COMB_NOX
    debugValues(model=MODEL, term=TERM_ID,
                diesel=diesel_value,
                gasoline=gasoline_value)
    return [_emission(diesel_value + gasoline_value)]


def _should_run(cycle: dict):
    diesel_values, gasoline_values = _get_fuel_values(cycle)
    has_diesel = len(diesel_values) > 0
    has_gasoline = len(gasoline_values) > 0

    logRequirements(model=MODEL, term=TERM_ID,
                    has_diesel=has_diesel,
                    has_gasoline=has_gasoline)

    should_run = any([has_diesel, has_gasoline])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, diesel_values, gasoline_values


def run(cycle: dict):
    should_run, diesel_values, gasoline_values = _should_run(cycle)
    return _run(diesel_values, gasoline_values) if should_run else []
