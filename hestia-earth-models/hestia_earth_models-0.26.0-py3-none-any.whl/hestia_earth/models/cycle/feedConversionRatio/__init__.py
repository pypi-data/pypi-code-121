from hestia_earth.schema import PracticeStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.product import liveweight_produced
from .. import MODEL
from . import feedConversionRatioCarbon
from . import feedConversionRatioDryMatter
from . import feedConversionRatioEnergy
from . import feedConversionRatioFedWeight
from . import feedConversionRatioNitrogen

MODELS = [
    feedConversionRatioCarbon,
    feedConversionRatioDryMatter,
    feedConversionRatioEnergy,
    feedConversionRatioFedWeight,
    feedConversionRatioNitrogen
]


def _practice(term_id: str, value: float):
    practice = _new_practice(term_id)
    practice['value'] = [value]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def _run(cycle: dict, kg_liveweight: float):
    return [_practice(model.TERM_ID, model.run(cycle) / kg_liveweight) for model in MODELS]


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    kg_liveweight = liveweight_produced(products)

    logRequirements(model=MODEL, key='feedConversionRatio',
                    kg_liveweight=kg_liveweight)

    should_run = all([kg_liveweight])
    logShouldRun(MODEL, None, should_run, key='feedConversionRatio')
    return should_run, kg_liveweight


def run(cycle: dict):
    should_run, kg_liveweight = _should_run(cycle)
    return _run(cycle, kg_liveweight) if should_run else []
