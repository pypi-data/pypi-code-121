from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta_n
from hestia_earth.models.utils.excretaManagement import get_lookup_factor
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [
            {"@type": "Input", "term.termType": "excreta", "term.units": "kg N"}
        ],
        "practices": [
            {"@type": "Practice", "term.termType": "excretaManagement"}
        ]
    }
}
LOOKUPS = {
    "excretaManagement": "EF_NON-N"
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'noxToAirExcreta'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(excretaKgN: float, NO_N_EF: float):
    value = NO_N_EF * excretaKgN * get_atomic_conversion(Units.KG_NOX, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    excretaKgN = total_excreta_n(cycle.get('inputs', []))
    NO_N_EF = get_lookup_factor(cycle.get('practices', []), LOOKUPS['excretaManagement'])

    logRequirements(model=MODEL, term=TERM_ID,
                    excretaKgN=excretaKgN,
                    NO_N_EF=NO_N_EF)

    should_run = all([excretaKgN, NO_N_EF])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, excretaKgN, NO_N_EF


def run(cycle: dict):
    should_run, excretaKgN, NO_N_EF = _should_run(cycle)
    return _run(excretaKgN, NO_N_EF) if should_run else []
