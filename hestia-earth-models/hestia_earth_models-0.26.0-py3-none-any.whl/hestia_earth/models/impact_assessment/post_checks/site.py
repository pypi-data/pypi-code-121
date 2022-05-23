"""
Site

This model is run only if the [pre model](../pre_checks/site.md) has been run before.
This model will restore the `impactAssessment.site` as a "linked node"
(i.e. it will be set with only `@type`, `@id` and `name` keys).
"""
from hestia_earth.utils.model import linked_node

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "@id": ""
        }
    }
}
RETURNS = {
    "ImpactAssessment": {
        "site": {"@type": "Site"}
    }
}


def _run(impact: dict): return linked_node(impact.get('site'))


def _should_run(impact: dict):
    site_id = impact.get('site', {}).get('@id')
    run = site_id is not None
    return run


def run(impact: dict): return {**impact, **({'site': _run(impact)} if _should_run(impact) else {})}
