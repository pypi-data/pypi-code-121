"""
Product Value

This model calculates the `value` of the [Product](https://hestia.earth/schema/Product)
by taking an average from the `min` and `max` values.
"""
from hestia_earth.utils.tools import non_empty_list, list_average

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "min": "", "max": ""}]
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
MODEL_KEY = 'value'


def _run(product: dict):
    value = list_average(product.get('min') + product.get('max'))
    return {**product, MODEL_KEY: [value]}


def _should_run(product: dict):
    should_run = all([
        len(product.get(MODEL_KEY, [])) == 0,
        len(product.get('min', [])) > 0,
        len(product.get('max', [])) > 0
    ])
    return should_run


def run(cycle: dict):
    products = list(filter(_should_run, cycle.get('products', [])))
    return non_empty_list(map(_run, products))
