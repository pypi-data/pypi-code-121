"""
ecoinvent v3

This model calculates background emissions related to the production of Inputs from the ecoinvent database, version 3.
"""
from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.data.impact_assessment import ecoinventV3_impacts
from hestia_earth.models.utils.emission import _new_emission

REQUIREMENTS = {
    "Cycle": {
        "inputs": [
            {"@type": "Input", "value": "> 0"}
        ]
    }
}
RETURNS = {
    "Emission": [{
        "term": "",
        "value": "",
        "methodTier": "background",
        "statsDefinition": "modelled",
        "inputs": ""
    }]
}
MODEL = 'ecoinventV3'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['inputs'] = [input.get('term')]
    return emission


def _add_emission(term_id: str):
    def add(prev: dict, mapping: tuple):
        ecoinventName, coefficient = mapping
        emissions = ecoinventV3_impacts(ecoinventName)
        for id, value in emissions:
            # log run on each emission so we know it did run
            debugValues(model=MODEL, term=id, input=term_id, value=value, coefficient=coefficient)
            logShouldRun(MODEL, id, True, methodTier=TIER, input=term_id)
            prev[id] = prev.get(id, 0) + (value * coefficient)
        return prev
    return add


def _get_input_mappings(input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoinventMapping', model=MODEL, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    logRequirements(model=MODEL, term=term_id,
                    mappings=';'.join(mappings))
    return [(m.split(':')[0], float(m.split(':')[1])) for m in mappings]


def _run_input(input: dict):
    term_id = input.get('term', {}).get('@id')
    input_value = list_sum(input.get('value', []))
    mappings = _get_input_mappings(input)
    should_run = len(mappings) > 0
    logShouldRun(MODEL, term_id, should_run, methodTier=TIER)
    grouped_emissions = reduce(_add_emission(term_id), mappings, {}) if should_run else {}
    return [_emission(term_id, value * input_value, input) for term_id, value in grouped_emissions.items()]


def run(cycle: dict):
    inputs = [i for i in cycle.get('inputs', []) if list_sum(i.get('value', [])) > 0]
    return flatten(map(_run_input, inputs))
