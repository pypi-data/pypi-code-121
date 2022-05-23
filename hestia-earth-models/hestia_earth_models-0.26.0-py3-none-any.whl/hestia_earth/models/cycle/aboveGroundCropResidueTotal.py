from hestia_earth.schema import ProductStatsDefinition
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "practices": {"@type": "Practice", "term.@id": "residueRemoved"},
        "products": {"@type": "Product", "term.@id": "aboveGroundCropResidueRemoved"}
    }
}
RETURNS = {
    "Product": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'aboveGroundCropResidueTotal'


def _product(value: float):
    product = _new_product(TERM_ID, value)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(practice_value: float, value: float):
    value = 0 if value and practice_value == 0 else value / (practice_value / 100)
    return [_product(value)]


def _should_run(cycle: dict):
    removed_practice_value = find_term_match(cycle.get('practices', []), 'residueRemoved').get('value', [])
    has_residueRemoved = len(removed_practice_value) > 0
    removed_value = find_term_match(cycle.get('products', []), 'aboveGroundCropResidueRemoved').get('value', [])
    has_aboveGroundCropResidueRemoved = len(removed_value) > 0
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(model=MODEL, term=TERM_ID,
                    has_residueRemoved=has_residueRemoved,
                    has_aboveGroundCropResidueRemoved=has_aboveGroundCropResidueRemoved)

    should_run = all([term_type_incomplete, has_residueRemoved, has_aboveGroundCropResidueRemoved])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, list_sum(removed_practice_value), list_sum(removed_value)


def run(cycle: dict):
    should_run, removed_practice_value, removed_value = _should_run(cycle)
    return _run(removed_practice_value, removed_value) if should_run else []
