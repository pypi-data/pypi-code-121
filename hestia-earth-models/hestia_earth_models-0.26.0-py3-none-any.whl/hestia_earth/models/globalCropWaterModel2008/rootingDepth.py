from hestia_earth.schema import CycleFunctionalUnit, PropertyStatsDefinition, TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.property import _new_property
from hestia_earth.models.utils.term import get_irrigation_terms
from hestia_earth.models.utils.cycle import valid_site_type
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "functionalUnit": "1 ha",
        "products": [
            {"@type": "Product", "term.termType": "crop"}
        ],
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        },
        "optional": {
            "dataCompleteness.water": "",
            "inputs": [
                {"@type": "Input", "term.termType": "water"}
            ]
        }
    }
}
LOOKUPS = {
    "crop": ["Rooting_depth_irrigated_m", "Rooting_depth_rainfed_m", "Rooting_depth_average_m"]
}
RETURNS = {
    "Products": [{
        "properties": [{
            "@type": "Property",
            "value": "",
            "statsDefinition": "modelled"
        }]
    }]
}
TERM_ID = 'rootingDepth'


def _property(value: float, term: dict):
    prop = _new_property(term, MODEL)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.MODELLED.value
    return prop


def _get_input_value_from_term(inputs: list, term_id: str):
    return list_sum(find_term_match(inputs, term_id).get('value'))


def _get_value(cycle: dict, term: dict, irrigation_ids: list):
    term_id = term.get('@id', '')

    if cycle.get('dataCompleteness', {}).get('water', False):
        value = sum([_get_input_value_from_term(cycle.get('inputs', []), term_id) for term_id in irrigation_ids])

        # Assumes that if water data is complete and there are no data on irrigation then there was no irrigation.
        column = 'Rooting_depth_irrigated_m' if value >= 250 else 'Rooting_depth_rainfed_m'
    else:
        column = 'Rooting_depth_average_m'

    return safe_parse_float(get_crop_lookup_value(MODEL, term_id, column), None)


def _should_run_product(cycle: dict):
    irrigation_ids = get_irrigation_terms()

    def exec(product: dict):
        product_id = product.get('term', {}).get('@id')
        value = _get_value(cycle, product.get('term'), irrigation_ids)

        logRequirements(model=MODEL, term=product_id, property=TERM_ID,
                        value=value)

        should_run = all([
            find_term_match(product.get('properties', []), TERM_ID, None) is None,
            value is not None
        ])
        logShouldRun(MODEL, product_id, should_run, property=TERM_ID)
        return should_run, product, value
    return exec


def _run_cycle(products: list):
    term = download_hestia(TERM_ID)

    def run_product(values: tuple):
        product, value = values
        prop = _property(value, term) if term is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else product

    return non_empty_list(map(run_product, products))


def _should_run(cycle: dict):
    functional_unit = cycle.get('functionalUnit')
    is_unit_hectare = functional_unit == CycleFunctionalUnit._1_HA.value
    site_type_valid = valid_site_type(cycle)
    # only run on crops
    crop_products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    has_crop_products = len(crop_products) > 0

    logRequirements(model=MODEL, term=TERM_ID,
                    is_unit_hectare=is_unit_hectare,
                    site_type_valid=site_type_valid,
                    has_crop_products=has_crop_products)

    should_run = all([site_type_valid, is_unit_hectare, has_crop_products])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, crop_products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    products = list(map(_should_run_product(cycle), products)) if should_run else []
    products = [(product, value) for (should_run, product, value) in products if should_run]
    return _run_cycle(products) if len(products) > 0 else []
