from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.cycle import get_excreta_N_total
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL
from .utils import get_N_N2O_excreta_coeff_from_primary_product

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.excretaManagement": "True",
        "inputs": [{
            "@type": "Input",
            "term.termType": "excreta",
            "optional": {
                "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
            }
        }]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'n2OToAirExcretaDirect'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, N_total: float):
    coefficient = get_N_N2O_excreta_coeff_from_primary_product(cycle)
    value = N_total * coefficient * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


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
