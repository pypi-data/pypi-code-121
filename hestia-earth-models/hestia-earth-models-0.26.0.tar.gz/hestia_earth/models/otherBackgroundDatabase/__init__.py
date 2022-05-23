from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import logShouldRun, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import load_impacts

MODEL = 'otherBackgroundDatabase'
MODEL_AGGREGATED = 'hestiaAggregatedData'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict, model: str):
    # log run on each emission so we know it did run
    logShouldRun(model, term_id, True, methodTier=TIER, input=input.get('term', {}).get('@id'))
    value = list_sum(input.get('value', [0])) * value
    emission = _new_emission(term_id, model)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['inputs'] = [input.get('term')]
    return emission


def _emission_group(term_id: str):
    lookup = download_lookup('emission.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('inputProductionGroupId'))


def _group_emissions(impact: dict):
    def _group_by(prev: dict, emission: dict):
        term_id = emission.get('term', {}).get('@id')
        grouping = _emission_group(term_id)
        if grouping:
            prev[grouping] = prev.get(grouping, 0) + emission.get('value', 0)
        return prev

    emissions = impact.get('emissionsResourceUse', [])
    return reduce(_group_by, emissions, {})


def _run_input(input: dict):
    impact = input.get('impactAssessment')
    model = MODEL_AGGREGATED if impact.get('aggregated', False) else MODEL
    emissions = _group_emissions(impact)
    return [
        _emission(term_id, value, input, model) for term_id, value in emissions.items()
    ]


def run(_, cycle: dict):
    inputs = load_impacts(cycle.get('inputs', []))
    inputs = [i for i in inputs if list_sum(i.get('value', [])) > 0]
    logger.debug('model=%s, nb inputs=%s', MODEL, len(inputs))
    return flatten(map(_run_input, inputs))
