"""
Emissions

Creates an [Indicator](https://hestia.earth/schema/Indicator) for every [Emission](https://hestia.earth/schema/Emission)
contained within the [ImpactAssesment.cycle](https://hestia.earth/schema/ImpactAssessment#cycle).
It does this by dividing the Emission amount by the Product amount, and applying an allocation between co-products.
"""
from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.impact_assessment import get_product, convert_value_from_cycle
from hestia_earth.models.utils.indicator import _new_indicator
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
            "emissions": [{"@type": "Emission"}]
        }
    }
}
RETURNS = {
    "Indicator": [{
        "term": "",
        "value": "",
        "statsDefinition": "modelled"
    }]
}


def _indicator(product: dict):
    def run(emission: dict):
        emission_value = list_sum(emission.get('value', [0]))
        value = convert_value_from_cycle(product, emission_value)

        logShouldRun(MODEL, emission.get('term', {}).get('@id'), True)

        indicator = _new_indicator(emission.get('term', {}))
        indicator['value'] = value
        indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
        if 'methodModel' in emission:
            indicator['methodModel'] = emission['methodModel']
        if len(emission.get('inputs', [])):
            indicator['inputs'] = emission['inputs']
        return indicator
    return run


def _should_run_emission(emission: dict): return emission.get('deleted', False) is not True


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment)
    product_id = product.get('term', {}).get('@id')
    logRequirements(model=MODEL, key='emissions',
                    product=product_id)
    should_run = product_id is not None
    logShouldRun(MODEL, None, should_run, key='emissions')
    return should_run, product


def run(impact_assessment: dict):
    should_run, product = _should_run(impact_assessment)
    emissions = impact_assessment.get('cycle', {}).get('emissions', []) if should_run else []
    emissions = list(filter(_should_run_emission, emissions))
    return list(map(_indicator(product), emissions))
