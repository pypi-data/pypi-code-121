from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements, debugMissingLookup
from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.cropResidue": "False",
        "products": {
            "@type": "Product",
            "primary": "True",
            "term.termType": "crop",
            "value": "> 0"
        },
        "site": {
            "@type": "Site",
            "country": ""
        }
    }
}
LOOKUPS = {
    "crop": "cropGroupingResidue",
    "region-crop-cropGroupingResidue-removed": "using result from `cropGroupingResidue`"
}
RETURNS = {
    "Practice": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'residueRemoved'
LOOKUP_NAME = 'region-crop-cropGroupingResidue-removed.csv'


def _get_default_percent(term: dict, country_id: str):
    crop_grouping = get_lookup_value(term, 'cropGroupingResidue', model=MODEL, term=TERM_ID)
    percent = get_table_value(
        download_lookup(LOOKUP_NAME), 'termid', country_id, column_name(crop_grouping)
    ) if crop_grouping else None
    debugMissingLookup(LOOKUP_NAME, 'termid', country_id, crop_grouping, percent,
                       model=MODEL)
    logRequirements(model=MODEL, term=TERM_ID,
                    crop_grouping=crop_grouping,
                    country_id=country_id,
                    percent=percent)
    return safe_parse_float(percent, None)


def run(cycle: dict):
    primary_product = find_primary_product(cycle)
    term = primary_product.get('term', {})
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    value = _get_default_percent(term, country_id)
    return None if value is None else value * 100
