"""
This model calculates the scarcity weighted water use based on the geospatial AWARE model
(see UNEP (2016); Boulay et al (2016); Boulay et al (2020); EC-JRC (2017)).
"""
from hestia_earth.schema import IndicatorStatsDefinition, SiteSiteType
from hestia_earth.utils.lookup import download_lookup, _get_single_table_value, column_name, get_table_value
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements, debugMissingLookup, logShouldRun
from hestia_earth.models.utils import sum_values, multiply_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import (
    convert_value_from_cycle, emission_value, get_product, get_site, get_region_id
)
from hestia_earth.models.utils.input import sum_input_impacts
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "or": {
                "awareWaterBasinId": "",
                "country": ""
            }
        },
        "optional": {
            "emissionsResourceUse": [{
                "@type": "Indicator",
                "term.@id": "freshwaterWithdrawalsDuringCycle"
            }]
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
    "@doc": "Different lookup files are used depending on the situation",
    "awareWaterBasinId": "using `awareWaterBasinId` and `YR_IRRI` (for `cropland` or `permanent pasture`) or `YR_NONIRRI`",  # noqa: E501
    "region-aware-factors": "using `region` and `YR_IRRI` (for `cropland` or `permanent pasture`) or `YR_NONIRRI`"
}
TERM_ID = 'scarcityWeightedWaterUse'
AWARE_KEY = 'awareWaterBasinId'
IRRIGATED_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.PERMANENT_PASTURE.value
]


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _get_factor_from_basinId(site: dict, aware_id: str):
    lookup_col = 'YR_IRRI' if site.get('siteType') in IRRIGATED_SITE_TYPES else 'YR_NONIRRI'
    value = _get_single_table_value(
        download_lookup(f"{AWARE_KEY}.csv"), column_name(AWARE_KEY), int(aware_id), column_name(lookup_col)
    )
    debugMissingLookup(f"{AWARE_KEY}.csv", AWARE_KEY, aware_id, lookup_col, value, model=MODEL, term=TERM_ID)
    return safe_parse_float(value, None)


def _get_factor_from_region(impact_assessment: dict, site: dict):
    region_id = get_region_id(impact_assessment)
    site_type = site.get('siteType')
    lookup_name = 'region-aware-factors.csv'
    lookup = download_lookup(lookup_name)
    lookup_suffix = 'unspecified' if not site_type else ('irri' if site_type in IRRIGATED_SITE_TYPES else 'non_irri')
    column = f"Agg_CF_{lookup_suffix}"
    value = get_table_value(lookup, 'termid', region_id, column_name(column))
    debugMissingLookup(lookup_name, 'termid', region_id, column, value, model=MODEL, term=TERM_ID)
    return safe_parse_float(value, None)


def _run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    fresh_water = emission_value(impact_assessment, 'freshwaterWithdrawalsDuringCycle')
    site = get_site(impact_assessment)
    aware_id = site.get(AWARE_KEY)
    factor = (
        _get_factor_from_basinId(site, aware_id) if aware_id else None
    ) or _get_factor_from_region(impact_assessment, site)
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID))

    logRequirements(model=MODEL, term=TERM_ID,
                    fresh_water=fresh_water,
                    aware_id=aware_id,
                    factor=factor,
                    inputs_value=inputs_value)

    value = sum_values([
        multiply_values([fresh_water, factor]),
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
