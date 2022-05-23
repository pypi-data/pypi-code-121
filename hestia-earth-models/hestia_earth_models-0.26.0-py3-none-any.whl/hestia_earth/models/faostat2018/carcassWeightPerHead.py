from hestia_earth.schema import PropertyStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, safe_parse_date

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.property import _new_property
from . import MODEL
from .utils import product_equivalent_value

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [
            {"@type": "Product", "term.termType": "animalProduct", "term.units": "kg carcass weight"}
        ],
        "site": {
            "@type": "Site",
            "country": ""
        }
    }
}
LOOKUPS = {
    "region-animalProduct-animalProductGroupingFAO-productionQuantity": "production quantity",
    "region-animalProduct-animalProductGroupingFAO-head": "number of heads"
}
RETURNS = {
    "Products": [{
        "properties": [{
            "@type": "Property",
            "value": "",
            "statsDefinition": "regions"
        }]
    }]
}
TERM_ID = 'carcassWeightPerHead'


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.REGIONS.value
    return prop


def _run(products: list, year: int, country: str):
    def run_product(product: dict):
        value = product_equivalent_value(product, year, country)
        prop = _property(value) if value else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else None

    return non_empty_list(map(run_product, products))


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    products = _filter_list_term_unit(products, Units.KG_CARCASS_WEIGHT)
    has_kg_carcass_products = len(products) > 0

    end_date = safe_parse_date(cycle.get('endDate'))
    year = end_date.year if end_date else None
    country = cycle.get('site', {}).get('country', {}).get('@id')

    logRequirements(model=MODEL, term=TERM_ID,
                    has_kg_carcass_products=has_kg_carcass_products,
                    year=year,
                    country=country)

    should_run = all([has_kg_carcass_products, year, country])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, products, year, country


def run(cycle: dict):
    should_run, products, year, country = _should_run(cycle)
    return _run(products, year, country) if should_run else []
