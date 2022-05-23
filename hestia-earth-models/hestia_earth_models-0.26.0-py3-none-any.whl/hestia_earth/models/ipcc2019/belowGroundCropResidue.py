from hestia_earth.models.utils.property import get_node_property
from hestia_earth.schema import ProductStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "products": {
            "@type": "Product",
            "term.termType": "crop",
            "value": "> 0",
            "optional": {
                "properties": [{"@type": "Property", "term.@id": "dryMatter"}]
            }
        }
    }
}
LOOKUPS = {
    "crop": ["IPCC_2019_Ratio_AGRes_YieldDM", "IPCC_2019_Ratio_BGRes_AGRes"]
}
RETURNS = {
    "Product": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'belowGroundCropResidue'
PROPERTY_KEY = 'dryMatter'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _get_crop_value(term_id: str, column: str):
    return safe_parse_float(get_crop_lookup_value(MODEL, term_id, column), None)


def _crop_product_value(crop: dict):
    term_id = crop.get('term', {}).get('@id')
    value = list_sum(crop.get('value'))
    dm = get_node_property(crop, PROPERTY_KEY).get('value', 0)
    yield_dm = _get_crop_value(term_id, LOOKUPS['crop'][0]) or 0
    ratio = _get_crop_value(term_id, LOOKUPS['crop'][1]) or 0
    debugValues(model=MODEL, term=TERM_ID,
                product=term_id,
                value=value,
                dryMatter=dm,
                ratio_yield_dm=yield_dm,
                ratio=ratio)
    return value * dm / 100 * yield_dm * ratio


def _run(products: list):
    value = sum(map(_crop_product_value, products))
    return [_product(value)]


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value', [0]))
    prop = get_node_property(product, PROPERTY_KEY).get('value')
    yield_dm = _get_crop_value(term_id, LOOKUPS['crop'][0])
    return all([value > 0, prop, yield_dm is not None])


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    products = list(filter(_should_run_product, products))
    has_crop_products = len(products) > 0
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(model=MODEL, term=TERM_ID,
                    has_crop_products=has_crop_products,
                    term_type_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete, has_crop_products])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
