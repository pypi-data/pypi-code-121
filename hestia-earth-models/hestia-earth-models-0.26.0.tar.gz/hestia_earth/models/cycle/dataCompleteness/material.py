"""
Material

This model checks if the `machinery` Input has been added and updates the
[Data Completeness](https://hestia.earth/schema/Completeness#material) value.
"""
from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logger
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.animalFeed": "False",
        "inputs": {"@type": "Input", "term.@id": "machineryInfrastructureDepreciatedAmountPerCycle"},
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        }
    }
}
RETURNS = {
    "Completeness": {
        "material": ""
    }
}
MODEL_KEY = 'material'


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    input = find_term_match(cycle.get('inputs', []), 'machineryInfrastructureDepreciatedAmountPerCycle', None)
    is_complete = all([site_type == SiteSiteType.CROPLAND.value, input])
    logger.debug('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
