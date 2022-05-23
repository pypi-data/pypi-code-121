"""
Site

This model is run only if the [pre model](../pre_checks/cycle.md) has been run before.
This model will restore the `cycle.site` as a "linked node"
(i.e. it will be set with only `@type`, `@id` and `name` keys).
"""
from hestia_earth.utils.model import linked_node

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "@id": ""
        }
    }
}
RETURNS = {
    "Cycle": {
        "site": {"@type": "Site"}
    }
}


def _run(cycle: dict): return linked_node(cycle.get('site'))


def _should_run(cycle: dict):
    site_id = cycle.get('site', {}).get('@id')
    run = site_id is not None
    return run


def run(cycle: dict): return {**cycle, **({'site': _run(cycle)} if _should_run(cycle) else {})}
