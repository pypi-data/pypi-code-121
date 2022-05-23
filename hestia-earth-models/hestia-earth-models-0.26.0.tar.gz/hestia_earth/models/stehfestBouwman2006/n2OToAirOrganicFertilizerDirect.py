from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_organic_fertilizer_N_total
from .n2OToAirSoilFlux import _get_value, _should_run
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.products": "",
        "inputs": [{
            "@type": "Input",
            "term.units": ["kg", "kg N"],
            "optional": {
                "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
            }
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
        },
        "optional": {
            "inputs": [{
                "@type": "Input",
                "term.termType": "organicFertilizer",
                "properties": [{"@type": "Property", "term.@id": "nitrogenContent"}]
            }]
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
    "crop": "cropGroupingStehfestBouwman",
    "ecoClimateZone": "STEHFEST_BOUWMAN_2006_N2O-N_FACTOR"
}
TERM_ID = 'n2OToAirOrganicFertilizerDirect'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, content_list_of_items: list, N_total: float):
    n2OToAirSoilFlux = _get_value(content_list_of_items, N_total, TERM_ID)
    value = get_organic_fertilizer_N_total(cycle)
    debugValues(model=MODEL, term=TERM_ID,
                noxToAirSoilFlux=n2OToAirSoilFlux,
                excreta_N_total=value)
    return [_emission(value * n2OToAirSoilFlux / N_total)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle, TERM_ID, TIER)
    return _run(cycle, content_list_of_items, N_total) if should_run else []
