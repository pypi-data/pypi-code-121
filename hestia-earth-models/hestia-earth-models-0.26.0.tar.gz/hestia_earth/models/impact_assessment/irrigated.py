"""
Organic

Detects if the [Cycle](https://hestia.earth/schema/ImpactAssessment#cycle) was irrigated.
"""
from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import is_irrigated
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "practices": [{"@type": "Practice", "term.termType": "waterRegime"}]
        }
    }
}
RETURNS = {
    "`true` if the `Cycle` was irrigated, `false` otherwise": ""
}
LOOKUPS = {
    "waterRegime": "irrigated"
}
MODEL_KEY = 'irrigated'


def run(impact: dict):
    value = is_irrigated(impact.get('cycle', {}))
    logger.debug('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value
