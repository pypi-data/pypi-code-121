from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import list_sum
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.utils.blank_node import get_total_value_converted

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "term.termType": "crop",
            "properties": {"@type": "Property", "term.@id": "dryMatter"}
        }]
    }
}
RETURNS = {
    "Practice": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'feedConversionRatioDryMatter'


def run(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.CROP)
    return list_sum(get_total_value_converted(inputs, 'dryMatter'))
