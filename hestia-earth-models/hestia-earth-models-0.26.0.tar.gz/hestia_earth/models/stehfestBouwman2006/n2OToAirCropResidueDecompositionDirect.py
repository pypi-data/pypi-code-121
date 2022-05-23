from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.product import residue_nitrogen
from hestia_earth.models.utils.crop import get_N2ON_fertilizer_coeff_from_primary_product
from hestia_earth.models.utils.emission import _new_emission
from .n2OToAirSoilFlux import _should_run
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": "cropResidue",
            "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
        }],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "term.@id": "totalNitrogenPerKgSoil"},
                {"@type": "Measurement", "term.@id": "organicCarbonPerKgSoil"},
                {"@type": "Measurement", "term.@id": "ecoClimateZone"},
                {"@type": "Measurement", "term.@id": "clayContent"},
                {"@type": "Measurement", "term.@id": "sandContent"},
                {"@type": "Measurement", "term.@id": "soilPh"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "crop": ["cropGroupingStehfestBouwman", "N2ON_FERT"]
}
TERM_ID = 'n2OToAirCropResidueDecompositionDirect'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict):
    N_total = residue_nitrogen(cycle.get('products', []))
    coefficient = get_N2ON_fertilizer_coeff_from_primary_product(MODEL, cycle)
    debugValues(model=MODEL, term=TERM_ID,
                coefficient=coefficient,
                N_total=N_total)
    value = N_total * coefficient * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def run(cycle: dict):
    should_run, *args = _should_run(cycle, TERM_ID, TIER)
    return _run(cycle) if should_run else []
