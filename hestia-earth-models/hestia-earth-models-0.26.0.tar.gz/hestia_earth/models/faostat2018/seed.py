from hestia_earth.schema import InputStatsDefinition
from hestia_earth.utils.lookup import download_lookup
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": "crop",
            "value": "> 0"
        }],
        "completeness.other": "False",
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        }
    }
}
LOOKUPS = {
    "crop": ["Seed_Output_kg_avg", "Seed_Output_kg_sd"]
}
RETURNS = {
    "Input": [{
        "value": "",
        "sd": "",
        "statsDefinition": "regions"
    }]
}
TERM_ID = 'seed'


def _input(value: float, sd: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    input['statsDefinition'] = InputStatsDefinition.REGIONS.value
    if sd > 0:
        input['sd'] = [sd]
    return input


def _run_product(product: dict):
    term = product.get('term', {})
    product_value = list_sum(product.get('value', []))
    value = safe_parse_float(get_lookup_value(term, 'Seed_Output_kg_avg', model=MODEL, term=TERM_ID)) * product_value
    sd = safe_parse_float(get_lookup_value(term, 'Seed_Output_kg_sd', model=MODEL, term=TERM_ID))
    return value, sd


def _run(products: list):
    values = list(map(_run_product, products))
    total_value = list_sum([value for value, _ in values])
    # TODO: we only fill-in sd for single values as the total value is complicated to calculate
    total_sd = values[0][1] if len(values) == 1 else 0
    return [_input(total_value, total_sd)] if total_value > 0 else []


def _should_run_product():
    lookup = download_lookup('crop.csv')

    def run(product: dict):
        term_id = product.get('term', {}).get('@id', '')
        product_value = list_sum(product.get('value', []))
        in_lookup = term_id in list(lookup.termid)
        return all([in_lookup, product_value > 0])
    return run


def _should_run(cycle: dict):
    products = list(filter(_should_run_product(), cycle.get('products', [])))
    has_products = len(products) > 0
    product_ids = ';'.join([p.get('term', {}).get('@id') for p in products])
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)
    site_type_valid = valid_site_type(cycle)

    logRequirements(model=MODEL, term=TERM_ID,
                    has_products=has_products,
                    product_ids=product_ids,
                    site_type_valid=site_type_valid)

    should_run = all([site_type_valid, term_type_incomplete, has_products])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
