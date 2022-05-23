"""
Above Ground Crop Residue

This model returns the amounts and destinations of above ground crop residue, working in the following order:
1. [Above ground crop residue, removed](https://hestia.earth/term/aboveGroundCropResidueRemoved);
2. [Above ground crop residue, incorporated](https://hestia.earth/term/aboveGroundCropResidueIncorporated);
3. [Above ground crop residue, burnt](https://hestia.earth/term/aboveGroundCropResidueBurnt);
4. [Above ground crop residue, left on field](https://hestia.earth/term/aboveGroundCropResidueLeftOnField).
"""
from functools import reduce
from hestia_earth.schema import ProductStatsDefinition
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum, list_average

from hestia_earth.models.log import logRequirements, logShouldRun, logger
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from . import MODEL
from .residue import residueBurnt
from .residue import residueIncorporated
from .residue import residueRemoved

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False"
    }
}
RETURNS = {
    "Product": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'aboveGroundCropResidueLeftOnField,aboveGroundCropResidueBurnt,aboveGroundCropResidueIncorporated,aboveGroundCropResidueRemoved'  # noqa: E501
TOTAL_TERM_ID = 'aboveGroundCropResidueTotal'
MODELS = [
    {'term': 'aboveGroundCropResidueRemoved', 'practice': residueRemoved},
    {'term': 'aboveGroundCropResidueIncorporated', 'practice': residueIncorporated},
    {'term': 'aboveGroundCropResidueBurnt', 'practice': residueBurnt}
]
REMAINING_MODEL = 'aboveGroundCropResidueLeftOnField'


def _get_practice_value(term_id: str, cycle: dict) -> float:
    value = find_term_match(cycle.get('practices', []), term_id).get('value', [])
    return list_sum(value) / 100 if len(value) > 0 else None


def _product(term_id: str, value: float):
    product = _new_product(term_id, value, MODEL)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _should_run_model(model, cycle: dict, primary_product: dict):
    term_id = model.get('term')
    practice_value = _get_practice_value(model.get('practice').TERM_ID, cycle)
    has_product = find_term_match(cycle.get('products', []), term_id, None) is not None

    logRequirements(model=MODEL, term=term_id,
                    practice_value=practice_value,
                    primary_product=(primary_product or {}).get('@id'),
                    has_product=has_product)

    should_run = all([practice_value is not None, primary_product, not has_product])
    logShouldRun(MODEL, term_id, should_run)
    return should_run, practice_value


def _run_model(model, cycle: dict, primary_product: dict, total_value: float):
    should_run, practice_value = _should_run_model(model, cycle, primary_product)
    return total_value * practice_value if should_run else None


def _model_value(term_id: str, products: list):
    values = find_term_match(products, term_id).get('value', [])
    return list_average(values) if len(values) > 0 else 0


def _run(cycle: dict, total_values: list):
    products = cycle.get('products', [])
    primary_product = find_primary_product(cycle)
    total_value = list_average(total_values)
    # first, calculate the remaining value available after applying all user-uploaded data
    remaining_value = reduce(
        lambda prev, model: prev - _model_value(model.get('term'), products),
        MODELS + [{'term': REMAINING_MODEL}],
        total_value
    )

    values = []
    # then run every model in order up to the remaining value
    for model in MODELS:
        term_id = model.get('term')
        value = _run_model(model, cycle, primary_product, total_value)
        logger.debug('model=%s, term=%s, value=%s', MODEL, term_id, value)
        if remaining_value > 0 and value is not None and value >= 0:
            value = value if value < remaining_value else remaining_value
            values.extend([_product(term_id, value)])
            remaining_value = remaining_value - value
            if remaining_value == 0:
                logger.debug('model=%s, term=%s, no more residue - stopping', MODEL, term_id)
                break

    return values + [
        # whatever remains is "left on field"
        _product(REMAINING_MODEL, remaining_value)
    ] if remaining_value > 0 else values


def _should_run(cycle: dict):
    term_type_incomplete = _is_term_type_incomplete(cycle, TOTAL_TERM_ID)
    total_values = find_term_match(cycle.get('products', []), TOTAL_TERM_ID).get('value', [])
    has_aboveGroundCropResidueTotal = len(total_values) > 0

    should_run = all([has_aboveGroundCropResidueTotal, term_type_incomplete])
    for term_id in TERM_ID.split(','):
        logRequirements(model=MODEL, term=term_id,
                        term_type_incomplete=term_type_incomplete,
                        has_aboveGroundCropResidueTotal=has_aboveGroundCropResidueTotal)
        logShouldRun(MODEL, term_id, should_run)

    return should_run, total_values


def run(cycle: dict):
    should_run, total_values = _should_run(cycle)
    return _run(cycle, total_values) if should_run else []
