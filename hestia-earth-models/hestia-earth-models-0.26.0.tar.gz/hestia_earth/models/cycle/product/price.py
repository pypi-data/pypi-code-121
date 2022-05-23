"""
Product Price

Calculates the price of `crop` and `animalProduct` using FAO data.
"""
from hestia_earth.schema import TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.lookup import (
    get_table_value, column_name, download_lookup, extract_grouped_data, extract_grouped_data_closest_date
)
from hestia_earth.utils.tools import non_empty_list, safe_parse_float, safe_parse_date

from hestia_earth.models.log import debugMissingLookup, debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY
from hestia_earth.models.utils.crop import FAOSTAT_PRODUCTION_LOOKUP_COLUMN, get_crop_grouping_faostat_production
from hestia_earth.models.utils.animalProduct import FAO_LOOKUP_COLUMN, get_animalProduct_grouping_fao
from hestia_earth.models.utils.product import convert_animalProduct_to_unit
from .utils import lookup_share
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": ["crop", "animalProduct", "liveAnimal"]
        }],
        "site": {
            "@type": "Site",
            "country": ""
        }
    }
}
RETURNS = {
    "Product": [{
        "price": ""
    }]
}
LOOKUPS = {
    "@doc": "Depending on the primary product [termType](https://hestia.earth/schema/Product#term)",
    "crop": "cropGroupingFaostatProduction",
    "region-crop-cropGroupingFaostatProduction-price": "use value from above",
    "animalProduct": ["animalProductGroupingFAOEquivalent", "animalProductGroupingFAO", "liveAnimal"],
    "region-animalProduct-animalProductGroupingFAO-price": "use value from above",
    "region-animalProduct-animalProductGroupingFAO-averageCarcassWeight": "use value from above"
}
MODEL_KEY = 'price'
LOOKUP_NAME = {
    TermTermType.CROP.value: f"region-{TermTermType.CROP.value}-{FAOSTAT_PRODUCTION_LOOKUP_COLUMN}-price.csv",
    TermTermType.ANIMALPRODUCT.value: f"region-{TermTermType.ANIMALPRODUCT.value}-{FAO_LOOKUP_COLUMN}-price.csv"
}
LOOKUP_GROUPING = {
    TermTermType.CROP.value: get_crop_grouping_faostat_production,
    TermTermType.ANIMALPRODUCT.value: get_animalProduct_grouping_fao
}


def _term_grouping(term: dict): return LOOKUP_GROUPING.get(term.get('termType'), lambda *_: None)(MODEL, term)


def _lookup_data(
    term_id: str, grouping: str, country_id: str, year: int, term_type: str = None, lookup_name: str = None
):
    lookup_name = lookup_name or LOOKUP_NAME.get(term_type)
    lookup = download_lookup(lookup_name)
    price_data = get_table_value(lookup, 'termid', country_id, column_name(grouping)) if grouping else None
    debugMissingLookup(lookup_name, 'termid', country_id, grouping, price_data,
                       model=MODEL, term=term_id, key=MODEL_KEY)
    avg_price = extract_grouped_data(price_data, 'Average_price_per_tonne') if (
        price_data and 'Average_price_per_tonne' in price_data
    ) else (extract_grouped_data_closest_date(price_data, year) if year else None)
    return safe_parse_float(avg_price, None)


def _product(product: dict, value: float):
    # currency is required, but do not override if present
    # currency in lookup table is set to USD
    return {'currency': DEFAULT_CURRENCY, **product, MODEL_KEY: value}


def get_liveAnimal_lookup_values(product: dict, country_id: str, year: int = None):
    weight_lookup = 'region-animalProduct-animalProductGroupingFAO-averageCarcassWeight.csv'
    lookup = download_lookup('animalProduct.csv')
    term_id = product.get('term', {}).get('@id')
    animal_products = lookup[lookup[column_name('liveAnimal')] == term_id]['termid']
    # one live animal can be linked to many animal product, hence go one by one until we have a match
    for animal_product in animal_products:
        grouping = _term_grouping({
            '@id': animal_product,
            'termType': TermTermType.ANIMALPRODUCT.value
        })
        average_carcass_weight = _lookup_data(animal_product, grouping, country_id, year, lookup_name=weight_lookup)
        price = _lookup_data(term_id, grouping, country_id, year, term_type=TermTermType.ANIMALPRODUCT.value)
        if price and average_carcass_weight:
            return (animal_product, price / 1000, average_carcass_weight / 10000)
    return (None, None, None)


def _run_by_liveAnimal(product: dict, country_id: str, year: int = None):
    term_id = product.get('term', {}).get('@id')
    animal_product, price, carcass_weight = get_liveAnimal_lookup_values(product, country_id, year)

    animal_product = download_hestia(animal_product)
    price_per_carcass_weight = convert_animalProduct_to_unit({
        'term': animal_product,
        'value': [price]
    }, Units.KG_CARCASS_WEIGHT) if price else None

    debugValues(model=MODEL, term=term_id, key=MODEL_KEY, by='liveAnimal',
                price_from_lookup=price,
                carcass_weight=carcass_weight,
                price_per_carcass_weight=price_per_carcass_weight)

    value = price_per_carcass_weight * carcass_weight if all([price_per_carcass_weight, carcass_weight]) else None
    return None if value is None else _product(product, value)


def _should_run_product_by_liveAnimal(product: dict):
    product_term = product.get('term', {})
    term_id = product_term.get('@id')
    is_liveAnimal = product_term.get('termType') == TermTermType.LIVEANIMAL.value

    logRequirements(model=MODEL, term=term_id, key=MODEL_KEY, by='liveAnimal',
                    is_liveAnimal=is_liveAnimal)

    should_run = all([is_liveAnimal])
    logShouldRun(MODEL, term_id, should_run, key=MODEL_KEY, by='liveAnimal')
    return should_run


def _run_by_country(product: dict, country_id: str, year: int = None):
    product_term = product.get('term', {})
    term_id = product_term.get('@id')
    term_type = product_term.get('termType')

    # get the grouping used in region lookup
    grouping = _term_grouping(product_term)

    value = _lookup_data(term_id, grouping, country_id, year, term_type=term_type)
    # divide by 1000 to convert price per tonne to kg
    return None if value is None else _product(product, value / 1000)


def _should_run_product_by_country(product: dict):
    term_id = product.get('term', {}).get('@id')
    has_yield = len(product.get('value', [])) > 0
    not_already_set = MODEL_KEY not in product.keys()
    grouping = _term_grouping(product.get('term', {}))

    logRequirements(model=MODEL, term=term_id, key=MODEL_KEY, by='country',
                    has_yield=has_yield,
                    not_already_set=not_already_set,
                    grouping=grouping)

    should_run = all([not_already_set, has_yield, grouping])
    logShouldRun(MODEL, term_id, should_run, key=MODEL_KEY, by='country')
    return should_run


def _should_run_product_by_share_0(product: dict):
    term_id = product.get('term', {}).get('@id')
    share = lookup_share(MODEL_KEY, product)
    share_is_0 = share is not None and share == 0

    logRequirements(model=MODEL, term=term_id, key=MODEL_KEY, by='economicValueShare',
                    share_is_0=share_is_0)

    should_run = all([share_is_0])
    logShouldRun(MODEL, term_id, should_run, key=MODEL_KEY, by='economicValueShare')
    return should_run


def _should_run(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')

    logRequirements(model=MODEL, key=MODEL_KEY,
                    country_id=country_id)

    should_run = all([country_id])
    logShouldRun(MODEL, None, should_run, key=MODEL_KEY)
    return should_run, country_id


def run(cycle: dict):
    should_run, country_id = _should_run(cycle)
    end_date = safe_parse_date(cycle.get('endDate'))
    year = end_date.year if end_date else None
    products_share_0 = list(filter(_should_run_product_by_share_0, cycle.get('products', [])))
    return ((
        non_empty_list(map(
            lambda p: _run_by_liveAnimal(p, country_id, year),
            filter(_should_run_product_by_liveAnimal, cycle.get('products', []))
        )) +
        non_empty_list(map(
            lambda p: _run_by_country(p, country_id, year),
            filter(_should_run_product_by_country, cycle.get('products', []))
        ))
    ) if should_run else []) + list(map(lambda p: _product(p, 0), products_share_0))
