from functools import reduce
from hestia_earth.schema import PracticeStatsDefinition
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, logger
from hestia_earth.models.utils.practice import _new_practice
from .. import MODEL
from . import residueBurnt
from . import residueIncorporated
from . import residueLeftOnField
from . import residueRemoved

MODELS = [
    residueRemoved,
    residueIncorporated,
    residueBurnt
]
REMAINING_MODEL = residueLeftOnField


def _practice(term_id: str, value: float):
    practice = _new_practice(term_id, MODEL)
    practice['value'] = [value]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def _should_run_model(term_id: str, cycle: dict):
    should_run = find_term_match(cycle.get('practices', []), term_id, None) is None
    logShouldRun(MODEL, term_id, should_run)
    return should_run


def _run_model(model, cycle: dict, remaining_value: float):
    should_run = _should_run_model(model.TERM_ID, cycle)
    value = model.run(cycle) if should_run else None
    return None if value is None else value * remaining_value / 100


def _model_value(term_id: str, practices: list):
    value = find_term_match(practices, term_id).get('value', [0])
    return list_sum(value)


def _remainig_practice(model, value: float):
    term_id = model.TERM_ID
    logShouldRun(MODEL, term_id, True)
    return [_practice(term_id, value)]


def _run(cycle: dict):
    practices = cycle.get('practices', [])
    # first, calculate the remaining value available after applying all user-uploaded data
    remaining_value = reduce(
        lambda prev, model: prev - _model_value(model.TERM_ID, practices),
        MODELS + [REMAINING_MODEL],
        100
    )

    values = []
    # then runevery model in order up to the remaining value
    for model in MODELS:
        value = _run_model(model, cycle, remaining_value)
        logger.debug('model=%s, term=%s, value=%s', MODEL, model.TERM_ID, value)
        if remaining_value > 0 and value is not None and value > 0:
            value = value if value < remaining_value else remaining_value
            values.extend([_practice(model.TERM_ID, value)])
            remaining_value = remaining_value - value
            if remaining_value == 0:
                logger.debug('model=%s, term=%s, no more residue - stopping', MODEL, model.TERM_ID)
                break

    return values + _remainig_practice(REMAINING_MODEL, remaining_value) if remaining_value > 0 else values


def _should_run(cycle: dict):
    primary_product = find_primary_product(cycle)
    has_primary_product = primary_product is not None
    should_run = all([has_primary_product])

    for model in MODELS:
        logRequirements(model=MODEL, term=model.TERM_ID,
                        has_primary_product=has_primary_product)
        logShouldRun(MODEL, model.TERM_ID, should_run)

    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
