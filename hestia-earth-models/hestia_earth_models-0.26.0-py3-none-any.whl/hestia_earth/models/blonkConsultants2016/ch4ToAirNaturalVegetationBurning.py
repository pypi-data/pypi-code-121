from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import land_occupation_per_ha
from .utils import get_emission_factor
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": [
            {
                "@doc": "if the [cycle.functionalUnit](https://hestia.earth/schema/Cycle#functionalUnit) = 1 ha, additional properties are required",  # noqa: E501
                "cycleDuration": "",
                "products": {
                    "@type": "Product",
                    "primary": "True",
                    "value": "> 0",
                    "economicValueShare": "> 0"
                },
                "site": {
                    "@type": "Site",
                    "measurements": {"@type": "Measurement", "term.@id": "fallowCorrection"}
                }
            },
            {
                "@doc": "for orchard crops, additional properties are required",
                "inputs": [
                    {"@type": "Input", "term.@id": "saplings"}
                ],
                "practices": [
                    {"@type": "Practice", "term.@id": "nurseryDuration"},
                    {"@type": "Practice", "term.@id": "orchardBearingDuration"},
                    {"@type": "Practice", "term.@id": "orchardDensity"},
                    {"@type": "Practice", "term.@id": "orchardDuration"},
                    {"@type": "Practice", "term.@id": "rotationDuration"}
                ]
            }
        ],
        "site": {
            "@type": "Site",
            "country": ""
        }
    }
}
LOOKUPS = {
    "crop": "cropGroupingFaostatArea",
    "region-crop-cropGroupingFaostatArea-ch4forestBiomassBurning": "use crop grouping above or default to site.siteType"
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'ch4ToAirNaturalVegetationBurning'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(land_occupation: float, ch4_forest_biomass_burning: float):
    value = land_occupation * ch4_forest_biomass_burning
    return [_emission(value)]


def _should_run(cycle: dict):
    land_occupation = land_occupation_per_ha(MODEL, TERM_ID, cycle)
    ch4_forest_biomass_burning = get_emission_factor(cycle, 'ch4forestBiomassBurning')

    logRequirements(model=MODEL, term=TERM_ID,
                    land_occupation=land_occupation,
                    ch4_forest_biomass_burning=ch4_forest_biomass_burning)

    should_run = all([land_occupation, ch4_forest_biomass_burning is not None])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, land_occupation, ch4_forest_biomass_burning


def run(cycle: dict):
    should_run, land_occupation, ch4_forest_biomass_burning = _should_run(cycle)
    return _run(land_occupation, ch4_forest_biomass_burning) if should_run else []
