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
    "crop": ["cropGroupingResidue", "Combustion_Factor_crop_residue"],
    "region-crop-cropGroupingResidue-burnt": "using result from `cropGroupingResidue`"
}
RETURNS = {
    "Practice": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'residueBurnt'
LOOKUP_NAME = 'region-crop-cropGroupingResidue-burnt.csv'


def _get_default_percent(term: dict, country_id: str):
    crop_grouping = get_lookup_value(term, 'cropGroupingResidue', model=MODEL, term=TERM_ID)
    lookup = download_lookup(LOOKUP_NAME)
    percent = safe_parse_float(
        get_table_value(lookup, 'termid', country_id, column_name(crop_grouping)), None
    ) if crop_grouping else None
    debugMissingLookup(LOOKUP_NAME, 'termid', country_id, crop_grouping, percent, model=MODEL)
    comb_factor = safe_parse_float(get_lookup_value(term, 'Combustion_Factor_crop_residue', model=MODEL, term=TERM_ID))
    logRequirements(model=MODEL, term=TERM_ID,
                    crop_grouping=crop_grouping,
                    country_id=country_id,
                    percent=percent,
                    comb_factor=comb_factor)
    return percent if comb_factor is None or percent is None else percent * comb_factor


def run(cycle: dict):
    primary_product = find_primary_product(cycle)
    term = primary_product.get('term', {})
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    value = _get_default_percent(term, country_id)
    return None if value is None else value * 100
