"""
Product Revenue

This model calculates the revenue of each product by multiplying the yield with the revenue.
- In the case the product `value` is `0`, the `revenue` will be set to `0`.
- In the case the product `price` is `0`, the `revenue` will be set to `0`.
"""
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY
from hestia_earth.models.utils.cycle import default_currency
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "price": "",
            "optional": {
                "value": ""
            }
        }]
    }
}
RETURNS = {
    "Product": [{
        "revenue": "",
        "currency": "defaults to USD if multiple currencies are used"
    }]
}
MODEL_KEY = 'revenue'


def _run(currency: str = DEFAULT_CURRENCY):
    def run(product: dict):
        value = list_sum(product.get('value', [0])) * product.get('price', 0)
        return {'currency': currency, **product, MODEL_KEY: value}
    return run


def _should_run(product: dict):
    term_id = product.get('term', {}).get('@id')
    has_yield = len(product.get('value', [])) > 0
    has_price = product.get('price', 0) > 0
    has_yield_and_price = has_yield and has_price
    is_yield_0 = list_sum(product.get('value', []), -1) == 0
    is_price_0 = product.get('price', -1) == 0
    not_already_set = MODEL_KEY not in product.keys()

    logRequirements(model=MODEL, term=term_id, key=MODEL_KEY,
                    not_already_set=not_already_set,
                    has_yield_and_price=has_yield_and_price,
                    is_yield_0=is_yield_0,
                    is_price_0=is_price_0)

    should_run = all([
        not_already_set,
        any([has_yield_and_price, is_yield_0, is_price_0])
    ])
    logShouldRun(MODEL, term_id, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict):
    products = list(filter(_should_run, cycle.get('products', [])))
    return non_empty_list(map(_run(default_currency(cycle)), products))
