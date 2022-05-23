"""
Organic

Detects if the [Cycle](https://hestia.earth/schema/ImpactAssessment#cycle) has an organic label.
"""
from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import is_organic
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "practices": [{"@type": "Practice", "term.termType": "standardsLabels"}]
        }
    }
}
RETURNS = {
    "`true` if the `Cycle` has an organic label, `false` otherwise": ""
}
LOOKUPS = {
    "standardLabels": "isOrganic"
}
MODEL_KEY = 'organic'


def run(impact: dict):
    value = is_organic(impact.get('cycle', {}))
    logger.debug('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value
