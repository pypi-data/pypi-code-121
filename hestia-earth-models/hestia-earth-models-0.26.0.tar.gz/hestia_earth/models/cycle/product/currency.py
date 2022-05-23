"""
Product Currency

Converts all the currencies to `USD` using historical rates.
"""
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY, convert
from .. import MODEL
from .revenue import _run as run_revenue

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [{"@type": "Product", "price": "", "currency": "not in USD"}]
    }
}
RETURNS = {
    "Product": [{
        "currency": "USD",
        "price": "in USD",
        "revenue": "in USD"
    }]
}
MODEL_KEY = 'currency'


def _run_product(date: str):
    def run(product: dict):
        price = convert(product.get('price'), product.get('currency'), date)
        return None if price is None else run_revenue()({**product, 'currency': DEFAULT_CURRENCY, 'price': price})
    return run


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    currency = product.get('currency')
    currency_not_USD = currency is not None and currency != DEFAULT_CURRENCY
    price = product.get('price')
    has_price = price is not None

    logRequirements(model=MODEL, term=term_id, key=MODEL_KEY,
                    currency_not_USD=currency_not_USD,
                    has_price=has_price)

    should_run = all([currency_not_USD, has_price])
    logShouldRun(MODEL, term_id, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict):
    products = list(filter(_should_run_product, cycle.get('products', [])))
    return non_empty_list(map(_run_product(cycle.get('endDate')), products))
