"""
Machinery gradually depreciates over multiple production Cycles until it reaches the
[end of its life](https://hestia.earth/schema/Infrastructure#endDate).
As a rough rule, the more the machinery is used, the faster it depreciates.
Machinery use can be proxied for by the amount of fuel used.
From 139 processes in [AGRIBALYSE](https://agribalyse.ademe.fr/), the ratio of machinery depreciated per unit of
fuel consumed (kg machinery kg diesel–1) was established.
Recognizing that farms in less developed countries have poorer access to capital and maintain farm machinery for longer,
the machinery-to-diesel ratio was doubled in countries with a [Human Development Index](http://hdr.undp.org/en/data)
of less than 0.8.
"""
from hestia_earth.schema import InputStatsDefinition
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.productivity import _get_productivity, PRODUCTIVITY
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.term import get_liquid_fuel_terms
from hestia_earth.models.utils.site import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "term.termType": "fuel"
        }],
        "completeness.material": "False",
        "site": {
            "@type": "Site",
            "country": "",
            "siteType": ["cropland", "permanent pasture"]
        }
    }
}
LOOKUPS = {
    "region": "HDI"
}
RETURNS = {
    "Input": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'machineryInfrastructureDepreciatedAmountPerCycle'


def _input(value: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    input['statsDefinition'] = InputStatsDefinition.MODELLED.value
    return input


def _get_input_value_from_term(inputs: list, term_id: str):
    val = find_term_match(inputs, term_id, None)
    return val.get('value', [0])[0] if val is not None else 0


def get_value(country: dict, cycle: dict):
    liquid_fuels = get_liquid_fuel_terms()
    productivity_key = _get_productivity(country)
    machinery_usage = 11.5 if productivity_key == PRODUCTIVITY.HIGH else 23
    fuel_use = sum([_get_input_value_from_term(cycle.get('inputs', []), term_id) for term_id in liquid_fuels])
    return fuel_use/machinery_usage if fuel_use > 0 else None


def _run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    value = get_value(country, cycle)
    return [_input(value)] if value is not None else []


def _should_run(cycle: dict):
    site_type_valid = valid_site_type(cycle.get('site', {}))
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(model=MODEL, term=TERM_ID,
                    site_type_valid=site_type_valid,
                    term_type_incomplete=term_type_incomplete)

    should_run = all([site_type_valid, term_type_incomplete])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
