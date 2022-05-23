from hestia_earth.schema import IndicatorStatsDefinition

from hestia_earth.models.log import logger, logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values, multiply_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import (
    convert_value_from_cycle, emission_value, get_product, get_site
)
from hestia_earth.models.utils.input import sum_input_impacts
from .utils import get_region_factor
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "country": "",
            "ecoregion": ""
        },
        "cycle": {
            "@type": "Cycle",
            "products": {
                "@type": "Product",
                "primary": "True",
                "value": "> 0",
                "economicValueShare": "> 0"
            }
        },
        "optional": {
            "emissionsResourceUse": [
                {"@type": "Indicator", "term.@id": "landTransformationFromForest20YearAverageDuringCycle"},
                {"@type": "Indicator", "term.@id": "landTransformationFromOtherNaturalVegetation20YearAverageDuringCycle"}  # noqa: E501
            ]
        }
    }
}
RETURNS = {
    "Indicator": {
        "value": "",
        "statsDefinition": "modelled"
    }
}
LOOKUPS = {
    "@doc": "Different lookup files are used depending on the situation",
    "ecoregion-factors": "using `ecoregion` and `TAXA_AGGREGATED_Median_transformation` columns",
    "region-ecoregion-factors": "using `region` and `TAXA_AGGREGATED_Median_transformation` columns"
}
TERM_ID = 'biodiversityLossLandTransformation'
TRANSFORMATION_TERM_IDS = [
    'landTransformationFromForest20YearAverageDuringCycle',
    'landTransformationFromOtherNaturalVegetation20YearAverageDuringCycle'
]


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _value(impact_assessment: dict, term_id: str):
    value = emission_value(impact_assessment, term_id)
    logger.debug('term=%s, node=%s, value=%s, coefficient=%s', TERM_ID, term_id, value, 1)
    return value


def _run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    landTransformation = sum_values([_value(impact_assessment, term_id) for term_id in TRANSFORMATION_TERM_IDS])
    factor = get_region_factor(TERM_ID, impact_assessment, 'transformation')
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID))
    logRequirements(model=MODEL, term=TERM_ID,
                    landTransformation=landTransformation,
                    factor=factor,
                    inputs_value=inputs_value)
    value = sum_values([
        multiply_values([landTransformation, factor]),
        inputs_value
    ])
    return _indicator(value)


def _should_run(impact_assessment: dict):
    site = get_site(impact_assessment)
    # does not run without a site as data is geospatial
    should_run = all([site])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run


def run(impact_assessment: dict):
    return _run(impact_assessment) if _should_run(impact_assessment) else None
