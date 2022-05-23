from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugMissingLookup, logRequirements
from hestia_earth.models.utils.impact_assessment import get_site, get_region_id
from hestia_earth.models.utils.crop import get_crop_grouping_fao
from . import MODEL


def _lookup_value(term_id: str, lookup_name: str, col_match: str, col_val: str, column: str):
    value = get_table_value(download_lookup(f"{lookup_name}.csv"), col_match, col_val, column)
    debugMissingLookup(f"{lookup_name}.csv", col_match, col_val, column, value, model=MODEL, term=term_id)
    return safe_parse_float(value)


def get_region_factor(term_id: str, impact_assessment: dict, factor: str):
    product = impact_assessment.get('product')
    region_id = get_region_id(impact_assessment)
    ecoregion = get_site(impact_assessment).get('ecoregion')
    lookup_name = 'ecoregion-factors' if ecoregion else 'region-ecoregion-factors' if region_id else None
    col = 'ecoregion' if ecoregion else 'termid' if region_id else None
    col_val = ecoregion or region_id
    try:
        grouping = get_crop_grouping_fao(MODEL, product)
        column = column_name(f"{grouping}_TAXA_AGGREGATED_Median_{factor}")
        logRequirements(model=MODEL, term=term_id,
                        factor=factor,
                        product=product.get('@id'),
                        crop_grouping=grouping)
        return _lookup_value(term_id, lookup_name, col, col_val, column) if grouping and lookup_name else 0
    except Exception:
        return 0
