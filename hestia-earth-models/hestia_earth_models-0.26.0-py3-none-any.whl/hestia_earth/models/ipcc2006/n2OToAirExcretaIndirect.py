from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.cycle import get_excreta_N_total
from hestia_earth.models.utils.emission import _new_emission
from .utils import get_nh3_no3_nox_to_n, COEFF_NH3NOX_N2O, COEFF_NO3_N2O
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.excretaManagement": "True",
        "inputs": [{
            "@type": "Input",
            "term.termType": "excreta",
            "optional": {
                "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
            }
        }],
        "emissions": [
            {"@type": "Emission", "term.@id": "no3ToGroundwaterExcreta"},
            {"@type": "Emission", "term.@id": "nh3ToAirExcreta"},
            {"@type": "Emission", "term.@id": "noxToAirExcreta"}
        ]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'n2OToAirExcretaIndirect'
TIER = EmissionMethodTier.TIER_1.value
NO3_TERM_ID = 'no3ToGroundwaterExcreta'
NH3_TERM_ID = 'nh3ToAirExcreta'
NOX_TERM_ID = 'noxToAirExcreta'


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, N_total: float):
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)
    debugValues(model=MODEL, term=TERM_ID,
                no3_n=no3_n,
                nh3_n=nh3_n,
                nox_n=nox_n)
    value = COEFF_NH3NOX_N2O * (
        N_total * 0.2 if nox_n == 0 or nh3_n == 0 else nh3_n + nox_n
    ) + COEFF_NO3_N2O * (
        N_total * 0.3 if no3_n == 0 else no3_n
    )
    return [_emission(value * get_atomic_conversion(Units.KG_N2O, Units.TO_N))]


def _should_run(cycle: dict):
    N_total = get_excreta_N_total(cycle)
    term_type_complete = _is_term_type_complete(cycle, {'termType': TermTermType.EXCRETAMANAGEMENT.value})

    logRequirements(model=MODEL, term=TERM_ID,
                    N_total=N_total,
                    term_type_complete=term_type_complete)

    should_run = any([N_total, term_type_complete])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_total


def run(cycle: dict):
    should_run, N_total = _should_run(cycle)
    return _run(cycle, N_total) if should_run else []
