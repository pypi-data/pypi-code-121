from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.product import abg_residue_nitrogen, abg_total_residue_nitrogen_content
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "products": [
                {"@type": "Product", "term.@id": "belowGroundCropResidue"},
                {
                    "@type": "Product",
                    "term.@id": "aboveGroundCropResidueTotal",
                    "properties": {"@type": "Property", "term.@id": "nitrogenContent"}
                }
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
TERM_ID = 'nh3ToAirCropResidueDecomposition'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(residue_nitrogen_abg: float, nitrogenContent: float):
    A = min([
        max([(0.38 * 1000 * nitrogenContent/100 - 5.44), 0]) / 100,
        17 / 100
    ])
    debugValues(model=MODEL, term=TERM_ID,
                A=A)
    value = A * residue_nitrogen_abg * get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    products = cycle.get('products', [])
    residue_nitrogen_abg = abg_residue_nitrogen(products)
    abg_residue_nitrogen_content = abg_total_residue_nitrogen_content(products)
    term_type_complete = _is_term_type_complete(cycle, {'termType': TermTermType.CROPRESIDUE.value})

    logRequirements(model=MODEL, term=TERM_ID,
                    residue_nitrogen=residue_nitrogen_abg,
                    abg_residue_nitrogen_content=abg_residue_nitrogen_content,
                    term_type_complete=term_type_complete)

    should_run = any([residue_nitrogen_abg > 0, term_type_complete])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, residue_nitrogen_abg, abg_residue_nitrogen_content


def run(cycle: dict):
    should_run, residue_nitrogen_abg, nitrogenContent = _should_run(cycle)
    return _run(residue_nitrogen_abg, nitrogenContent) if should_run else []
