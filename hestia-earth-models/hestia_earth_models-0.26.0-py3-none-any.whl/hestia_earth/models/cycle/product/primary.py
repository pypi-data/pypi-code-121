"""
Product Primary

Determines the primary product which is the product with the highest `economicValueShare`.
"""
from hestia_earth.models.log import logRequirements, logShouldRun
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "economicValueShare": ""}]
    }
}
RETURNS = {
    "Product": [{
        "primary": ""
    }]
}
MODEL_KEY = 'primary'


def _product(product: dict):
    return {**product, MODEL_KEY: True}


def _find_primary_product(products: list):
    # If only one product, primary = True
    if len(products) == 1:
        return products[0]

    # else primary product = the product with the largest economic value share
    else:
        max_products = sorted(
            list(filter(lambda p: 'economicValueShare' in p.keys(), products)),  # take only products with value
            key=lambda k: k.get('economicValueShare'),  # sort by value
            reverse=True  # take the first as top value
        )
        if len(max_products) > 0:
            return max_products[0]

    return None


def _run(products: list):
    primary = _find_primary_product(products)
    return [] if primary is None else [_product(primary)]


def _should_run(products: list):
    primary = next((p for p in products if p.get(MODEL_KEY, False) is True), None)
    has_primary_product = primary is None
    has_products = len(products) > 0

    logRequirements(model=MODEL, key=MODEL_KEY,
                    has_primary_product=has_primary_product,
                    has_products=has_products)

    should_run = all([has_products, has_primary_product])
    logShouldRun(MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict):
    products = cycle.get('products', [])
    return _run(products) if _should_run(products) else []
