"""
Other

This model checks if the `seed` or `saplings` Input has been added and updates the
[Data Completeness](https://hestia.earth/schema/Completeness#other) value.
"""
from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_term_match, find_primary_product

from hestia_earth.models.log import logger
from hestia_earth.models.utils.crop import is_orchard
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.other": "False",
        "inputs": [
            {"@type": "Input", "term.@id": ["seed", "saplings"]}
        ],
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        }
    }
}
RETURNS = {
    "Completeness": {
        "other": ""
    }
}
MODEL_KEY = 'other'


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    is_cropland = site_type == SiteSiteType.CROPLAND.value

    has_seed = find_term_match(cycle.get('inputs', []), 'seed', None)

    product = find_primary_product(cycle) or {}
    term_id = product.get('term', {}).get('@id')
    has_saplings = find_term_match(cycle.get('inputs', []), 'saplings', None) and is_orchard(MODEL, term_id)

    is_complete = all([is_cropland, has_seed or has_saplings])
    logger.debug('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
