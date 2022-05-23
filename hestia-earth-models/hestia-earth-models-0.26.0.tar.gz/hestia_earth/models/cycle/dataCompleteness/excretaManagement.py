"""
Excreta management

This model checks if the site is a cropland and updates the
[Data Completeness](https://hestia.earth/schema/Completeness#excretaManagement) value.
"""
from hestia_earth.schema import SiteSiteType

from hestia_earth.models.log import logger
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.excretaManagement": "False",
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        }
    }
}
RETURNS = {
    "Completeness": {
        "excretaManagement": ""
    }
}
MODEL_KEY = 'excretaManagement'


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    is_complete = all([site_type == SiteSiteType.CROPLAND.value])
    logger.debug('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
