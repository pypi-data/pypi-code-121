from hestia_earth.schema import PropertyStatsDefinition
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.property import _new_property, get_node_property
from hestia_earth.models.utils.term import get_wood_fuel_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "term.termType": ["woodFuel", "woodPellets"],
            "properties": {"@type": "Property", "term.@id": "dryMatter"}
        }]
    }
}
RETURNS = {
    "Input": [{
        "properties": [{
            "@type": "Property",
            "value": "",
            "statsDefinition": "modelled"
        }]
    }]
}
TERM_ID = 'energyContentLowerHeatingValue'
PROPERTY_KEY = 'dryMatter'
DRY_VALUE = 19.2  # Bone dry wood has an energy content of 19.2 MJ/kg


def _property(value: float):
    prop = _new_property(TERM_ID)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.MODELLED.value
    return prop


def _run(inputs: list):
    def run_input(input: dict):
        dry_matter = get_node_property(input, PROPERTY_KEY).get('value')
        moisture_content = 100 - dry_matter
        value = DRY_VALUE - (0.2164 * moisture_content)
        return {**input, 'properties': input.get('properties', []) + [_property(round(value, 2))]}

    return non_empty_list(map(run_input, inputs))


def _should_run_input(input: dict):
    term_id = input.get('term', {}).get('@id')
    prop_value = get_node_property(input, PROPERTY_KEY, find_default_property=False).get('value')

    logRequirements(model=MODEL, term=term_id, property=TERM_ID,
                    dryMatter=prop_value)

    should_run = all([prop_value is not None])
    logShouldRun(MODEL, term_id, should_run, property=TERM_ID)
    return should_run


def run(cycle: dict):
    term_ids = get_wood_fuel_terms()
    inputs = [input for input in cycle.get('inputs', []) if input.get('term', {}).get('@id') in term_ids]
    inputs = list(filter(_should_run_input, inputs))
    return _run(inputs) if len(inputs) > 0 else []
