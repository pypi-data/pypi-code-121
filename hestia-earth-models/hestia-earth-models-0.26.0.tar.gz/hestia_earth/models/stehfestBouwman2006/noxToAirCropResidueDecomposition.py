from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils.emission import _new_emission
from .noxToAirSoilFlux import _should_run, _get_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "inputs": [{
                "@type": "Input",
                "term.units": ["kg", "kg N"],
                "optional": {
                    "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
                }
            }],
            "products": [{
                "@type": "Product",
                "term.termType": "cropResidue",
                "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
            }]
        },
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "term.@id": "totalNitrogenPerKgSoil"},
                {"@type": "Measurement", "term.@id": "ecoClimateZone"}
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
    "ecoClimateZone": "STEHFEST_BOUWMAN_2006_NOX-N_FACTOR"
}
TERM_ID = 'noxToAirCropResidueDecomposition'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(ecoClimateZone: str, nitrogenContent: float, N_total: float, residue: float):
    noxToAirSoilFlux = _get_value(ecoClimateZone, nitrogenContent, N_total, TERM_ID)
    debugValues(model=MODEL, term=TERM_ID,
                noxToAirSoilFlux=noxToAirSoilFlux)
    return [_emission(residue * noxToAirSoilFlux / N_total)]


def run(cycle: dict):
    should_run, ecoClimateZone, nitrogenContent, N_total, residue = _should_run(cycle, TERM_ID, TIER)
    return _run(ecoClimateZone, nitrogenContent, N_total, residue) if should_run else []
