from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

LOOKUP_COLUMN = 'global_economic_value_share'


def lookup_share(key: str, product: dict, default=None):
    return safe_parse_float(get_lookup_value(product.get('term', {}), LOOKUP_COLUMN, model=MODEL, key=key), default)
