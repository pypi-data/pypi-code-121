from hestia_earth.schema import ProductStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.property import get_node_property
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
    "crop": ["Crop_residue_intercept", "Crop_residue_slope"]
}
RETURNS = {
    "Product": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'aboveGroundCropResidueTotal'
PROPERTY_KEY = 'dryMatter'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _get_value_dm(product: dict, dm_percent: float):
    term_id = product.get('term', {}).get('@id', '')
    product_yield = list_sum(product.get('value', [0]))
    yield_dm = product_yield * (dm_percent / 100)

    # estimate the AG DM calculation
    slope = safe_parse_float(get_crop_lookup_value(MODEL, term_id, LOOKUPS['crop'][1]), None)
    intercept = safe_parse_float(get_crop_lookup_value(MODEL, term_id, LOOKUPS['crop'][0]), None)
    debugValues(model=MODEL, term=TERM_ID,
                yield_dm=yield_dm,
                dryMatter_percent=dm_percent,
                slope=slope,
                intercept=intercept)
    return None if slope is None or intercept is None else (yield_dm * slope + intercept * 1000)


def _run(product: dict, dm_property: dict):
    value = _get_value_dm(product, safe_parse_float(dm_property.get('value')))
    return [_product(value)] if value is not None else []


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value', [0]))
    return value > 0 and (
        safe_parse_float(get_crop_lookup_value(MODEL, term_id, LOOKUPS['crop'][0]), None) is not None
    )


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    products = list(filter(_should_run_product, products))
    single_crop_product = len(products) == 1
    dm_property = get_node_property(products[0], PROPERTY_KEY) if single_crop_product else {}
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(model=MODEL, term=TERM_ID,
                    single_crop_product=single_crop_product,
                    nb_products=len(products),
                    dryMatter=dm_property.get('value'),
                    term_type_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete, single_crop_product, dm_property])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run, products, dm_property


def run(cycle: dict):
    should_run, products, dm_property = _should_run(cycle)
    return _run(products[0], dm_property) if should_run else []
