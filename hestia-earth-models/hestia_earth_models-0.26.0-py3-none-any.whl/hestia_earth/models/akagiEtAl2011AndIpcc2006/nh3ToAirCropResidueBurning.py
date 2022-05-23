from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from .utils import _get_aboveGroundCropResidueBurnt_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "products": [{
                "@type": "Product",
                "term.@id": "aboveGroundCropResidueBurnt"
            }],
            "dataCompleteness.cropResidue": "True"
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
TERM_ID = 'nh3ToAirCropResidueBurning'
TIER = EmissionMethodTier.TIER_1.value
DRY_MATTER_FACTOR_TO_NH3 = 2.17/1000


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(product_value: list):
    value = sum(product_value)
    return [_emission(value * DRY_MATTER_FACTOR_TO_NH3)]


def _should_run(cycle: dict):
    aboveGroundCropResidueBurnt_value = _get_aboveGroundCropResidueBurnt_value(cycle)
    has_aboveGroundCropResidueBurnt = len(aboveGroundCropResidueBurnt_value) > 0

    logRequirements(model=MODEL, term=TERM_ID,
                    has_aboveGroundCropResidueBurnt=has_aboveGroundCropResidueBurnt)

    should_run = all([has_aboveGroundCropResidueBurnt])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, aboveGroundCropResidueBurnt_value


def run(cycle: dict):
    should_run, aboveGroundCropResidueBurnt_value = _should_run(cycle)
    return _run(aboveGroundCropResidueBurnt_value) if should_run else []
