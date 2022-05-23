"""
Input Value

This model calculates the `value` of the [Input](https://hestia.earth/schema/Input)
by taking an average from the `min` and `max` values.
"""
from hestia_earth.utils.tools import non_empty_list, list_average

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{"@type": "Input", "min": "", "max": ""}]
    }
}
RETURNS = {
    "Input": [{
        "value": ""
    }]
}
MODEL_KEY = 'value'


def _run(input: dict):
    value = list_average(input.get('min') + input.get('max'))
    return {**input, MODEL_KEY: [value]}


def _should_run(input: dict):
    should_run = all([
        len(input.get(MODEL_KEY, [])) == 0,
        len(input.get('min', [])) > 0,
        len(input.get('max', [])) > 0
    ])
    return should_run


def run(cycle: dict):
    inputs = list(filter(_should_run, cycle.get('inputs', [])))
    return non_empty_list(map(_run, inputs))
