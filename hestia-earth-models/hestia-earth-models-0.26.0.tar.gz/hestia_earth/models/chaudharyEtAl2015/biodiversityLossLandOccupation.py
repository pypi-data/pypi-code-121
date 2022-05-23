from hestia_earth.schema import IndicatorStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values, multiply_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import convert_value_from_cycle, get_product, get_site
from hestia_earth.models.utils.cycle import land_occupation_per_kg
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
            },
            "or": [
                {
                    "@doc": "if the [cycle.functionalUnit](https://hestia.earth/schema/Cycle#functionalUnit) = 1 ha, additional properties are required",  # noqa: E501
                    "cycleDuration": "",
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
    "ecoregion-factors": "using `ecoregion` and `TAXA_AGGREGATED_Median_occupation` columns",
    "region-ecoregion-factors": "using `region` and `TAXA_AGGREGATED_Median_occupation` columns"
}
TERM_ID = 'biodiversityLossLandOccupation'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    site = get_site(impact_assessment)
    cycle['site'] = site
    landOccupation = land_occupation_per_kg(MODEL, TERM_ID, cycle, product)
    factor = get_region_factor(TERM_ID, impact_assessment, 'occupation')
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID))
    logRequirements(model=MODEL, term=TERM_ID,
                    landOccupation=landOccupation,
                    factor=factor,
                    inputs_value=inputs_value)
    value = sum_values([
        multiply_values([landOccupation, factor]),
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
