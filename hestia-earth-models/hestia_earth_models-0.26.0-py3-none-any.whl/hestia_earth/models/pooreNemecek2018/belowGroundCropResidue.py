from hestia_earth.schema import ProductStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.cropResidue": "False",
        "products": {
            "@type": "Product",
            "primary": "True",
            "term.termType": "crop"
        }
    }
}
LOOKUPS = {
    "crop": "Default_bg_dm_crop_residue"
}
RETURNS = {
    "Product": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'belowGroundCropResidue'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _get_lookup_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(MODEL, term_id, LOOKUPS['crop']), None)


def _run(product: dict):
    value = _get_lookup_value(product)
    return [_product(value)]


def _should_run_product(product: dict):
    value = list_sum(product.get('value', [0]))
    lookup_value = _get_lookup_value(product)
    return value > 0 and lookup_value is not None


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    products = list(filter(_should_run_product, products))
    single_crop_product = len(products) == 1
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(model=MODEL, term=TERM_ID,
                    single_crop_product=single_crop_product,
                    term_type_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete, single_crop_product])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products[0]) if should_run else []
