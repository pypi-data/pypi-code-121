"""
Live Animal

This model calculates the amount of live animal produced during a Cycle, based on the amount of animal product.
"""
from hestia_earth.schema import TermTermType, ProductStatsDefinition
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": {
            "@type": "Product",
            "term.termType": "animalProduct",
            "properties": {
                "@type": "Property",
                "term.@id": [
                    "liveweightPerHead", "carcassWeightPerHead",
                    "readyToCookWeightPerHead", "dressedCarcassWeightPerHead"
                ]
            }
        }
    }
}
RETURNS = {
    "Product": [{
        "term.termType": "liveAnimal",
        "value": "",
        "statsDefinition": "modelled"
    }]
}
KEY = 'liveAnimal'


def _product(term: str, value: float):
    product = _new_product(term, value)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(liveAnimal: str, product_value: dict, propertyPerHead: float):
    value = product_value / propertyPerHead
    return [_product(liveAnimal, value)] if value else []


def _get_liveAnimal(product: dict):
    return get_lookup_value(product.get('term', {}), KEY, model=MODEL, key=KEY)


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    product_value = list_sum(product.get('value', []))
    is_animalProduct = product.get('term', {}).get('termType') == TermTermType.ANIMALPRODUCT.value
    propertyPerHead = safe_parse_float(
        next(
            (p for p in product.get('properties', []) if p.get('term', {}).get('@id').endswith('PerHead')), {}
        ).get('value'), 0
    )

    # make sure the `liveAnimal` is not already present as a product
    liveAnimal = _get_liveAnimal(product)
    has_liveAnimal = find_term_match(cycle.get('products', []), liveAnimal, None) is not None

    logRequirements(model=MODEL, key=KEY,
                    is_animalProduct=is_animalProduct,
                    liveAnimal=liveAnimal,
                    has_liveAnimal=has_liveAnimal,
                    product_value=product_value,
                    propertyPerHead=propertyPerHead)

    should_run = all([is_animalProduct, liveAnimal, not has_liveAnimal, product_value, propertyPerHead])
    logShouldRun(MODEL, None, should_run, key=KEY)
    return should_run, liveAnimal, product_value, propertyPerHead


def run(cycle: dict):
    should_run, liveAnimal, product_value, propertyPerHead = _should_run(cycle)
    return _run(liveAnimal, product_value, propertyPerHead) if should_run else []
