from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import list_sum

from ..log import debugValues


def _node_value(node):
    value = node.get('value')
    return list_sum(value) if isinstance(value, list) else value


def _factor_value(lookup_name: str, lookup_col: str, term_id: str):
    lookup = download_lookup(lookup_name)

    def get_value(node: dict):
        node_term_id = node.get('term', {}).get('@id')
        value = _node_value(node)
        coefficient = get_table_value(lookup, 'termid', node_term_id, column_name(lookup_col))
        if value is not None and coefficient is not None:
            debugValues(term=term_id, node=node_term_id, value=value, coefficient=coefficient)
            return value * coefficient
        return None
    return get_value
