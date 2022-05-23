from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils.cycle import get_excreta_N_total
from hestia_earth.models.utils.emission import _new_emission
from .no3ToGroundwaterSoilFlux import _should_run, _get_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.products": "",
        "inputs": [{
            "@type": "Input",
            "term.termType": "excreta",
            "properties": [
                {"@type": "Property", "term.@id": "nitrogenContent"}
            ]
        }],
        "products": [{
            "@type": "Product",
            "term.termType": "excreta",
            "properties": [
                {"@type": "Property", "term.@id": "nitrogenContent"}
            ]
        }],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "term.@id": "clayContent"},
                {"@type": "Measurement", "term.@id": "sandContent"},
                {"@type": "Measurement", "term.@id": ["rainfallAnnual", "rainfallLongTermAnnualMean"]}
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
TERM_ID = 'no3ToGroundwaterExcreta'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, content_list_of_items: list):
    no3ToGroundwaterSoilFlux = _get_value(content_list_of_items, TERM_ID)
    value = get_excreta_N_total(cycle)
    debugValues(model=MODEL, term=TERM_ID,
                N_total=value)
    return [_emission(value * no3ToGroundwaterSoilFlux)]


def run(cycle: dict):
    should_run, content_list_of_items = _should_run(cycle, TERM_ID, TIER)
    return _run(cycle, content_list_of_items) if should_run else []
