from hestia_earth.schema import IndicatorStatsDefinition, TermTermType
from hestia_earth.utils.tools import list_sum, safe_parse_float
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product, convert_value_from_cycle, get_site
from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.input import sum_input_impacts
from hestia_earth.models.utils.crop import get_crop_grouping_fao
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {"@type": "Product"},
        "cycle": {
            "@type": "Cycle",
            "products": {
                "@type": "Product",
                "value": "> 0",
                "economicValueShare": "> 0"
            },
            "or": {
                "dataCompleteness.water": "True",
                "inputs": [{"@type": "Input", "term.termType": "water", "value": "> 0"}]
            }
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "crop": "cropGroupingFAO",
    "region": ["Conveyancing_Efficiency_Annual_crops", "Conveyancing_Efficiency_Permanent_crops"]
}
TERM_ID_CYCLE = 'freshwaterWithdrawalsDuringCycle'
TERM_ID_INPUTS = 'freshwaterWithdrawalsInputsProduction'
TERM_ID = 'freshwaterWithdrawalsDuringCycle,freshwaterWithdrawalsInputsProduction'


def _indicator(term_id: str, value: float):
    indicator = _new_indicator(term_id)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run_inputs(impact_assessment: dict, product: dict):
    cycle = impact_assessment.get('cycle', {})
    value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID_CYCLE))
    debugValues(model=MODEL, term=TERM_ID_INPUTS,
                value=value)
    return [] if value is None else [_indicator(TERM_ID_INPUTS, value)]


def _get_conveyancing_efficiency(impact_assessment: dict, product: dict):
    site = get_site(impact_assessment)
    country = impact_assessment.get('country', {}) or site.get('country', {})
    grouping = get_crop_grouping_fao(MODEL, product.get('term', {}))
    value = get_lookup_value(country, f"Conveyancing_Efficiency_{grouping}", model=MODEL, term=TERM_ID)
    debugValues(model=MODEL, term=TERM_ID_CYCLE,
                grouping=grouping,
                conveyancing_efficiency=value)
    return safe_parse_float(value, 1)


def _run(impact_assessment: dict, product: dict, irrigation: float):
    conveyancing = _get_conveyancing_efficiency(impact_assessment, product)
    # convert from m3 to litre
    value = convert_value_from_cycle(product, irrigation / conveyancing * 1000 if irrigation > 0 else 0)
    debugValues(model=MODEL, term=TERM_ID_CYCLE,
                value=value)
    return _indicator(TERM_ID_CYCLE, value)


def _get_irrigation(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    data_complete = _is_term_type_complete(cycle, {'termType': TermTermType.WATER.value})
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.WATER)
    value = list_sum(get_total_value(inputs))
    return None if len(inputs) == 0 and not data_complete else value


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment) or {}
    product_id = product.get('term', {}).get('@id')
    irrigation = _get_irrigation(impact_assessment)

    logRequirements(model=MODEL, term=TERM_ID_CYCLE,
                    product=product_id,
                    irrigation=irrigation)

    should_run = all([product_id, irrigation is not None])
    logShouldRun(MODEL, TERM_ID_CYCLE, should_run)

    logRequirements(model=MODEL, term=TERM_ID_INPUTS,
                    product=product_id)

    should_run_inputs = all([product])
    logShouldRun(MODEL, TERM_ID_INPUTS, should_run_inputs)

    return should_run, should_run_inputs, product, irrigation


def run(impact_assessment: dict):
    should_run, should_run_inputs, product, irrigation = _should_run(impact_assessment)
    return (
        [_run(impact_assessment, product, irrigation)] if should_run else []
    ) + (
        _run_inputs(impact_assessment, product) if should_run_inputs else []
    )
