"""
Site duration

This model calculates the `siteDuration` on the `Cycle` to the same value as `cycleDuration`
when only a single `Site` is present.
"""
from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "365",
        "none": {
            "otherSites": ""
        }
    }
}
RETURNS = {
    "a `number` or `None` if the `Cycle` has multiple `Sites`": ""
}
MODEL_KEY = 'siteDuration'


def _run(cycle: dict): return cycle.get('cycleDuration')


def _should_run(cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 0)
    has_other_sites = len(cycle.get('otherSites', [])) == 0

    logRequirements(model=MODEL, key=MODEL_KEY,
                    cycleDuration=cycleDuration,
                    has_other_sites=has_other_sites)

    should_run = all([cycleDuration > 0, has_other_sites])
    logShouldRun(MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else None
