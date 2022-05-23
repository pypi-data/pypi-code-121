"""
Site

Some Cycle models need a full version of the linked [Site](https://hestia.earth/schema/Site) to run.
This model will fetch the complete version of the [Site](https://hestia.earth/schema/Site) and include it.
"""
from hestia_earth.schema import SchemaType

from hestia_earth.models.utils import _load_calculated_node

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


def _run(cycle: dict): return _load_calculated_node(cycle.get('site', {}), SchemaType.SITE)


def _should_run(cycle: dict):
    site_id = cycle.get('site', {}).get('@id')
    run = site_id is not None
    return run


def run(cycle: dict): return {**cycle, **({'site': _run(cycle)} if _should_run(cycle) else {})}
