"""
Excreta (kg N)

This model uses a mass balance to calculate the total amount of excreta (as N) created by animals.
The inputs into the mass balance are the total amount of feed and the total amount of net primary production
in the water body.
The outputs of the mass balance are the weight of the animal and the excreta.
The formula is excreta = feed + NPP - animal.
If the mass balance fails
(i.e. [animal feed](https://hestia.earth/schema/Completeness#animalFeed) is not complete, see requirements below) for
[live aquatic species](https://hestia.earth/glossary?termType=liveAquaticSpecies),
the fomula is = total nitrogen content of the fish * 3.31.
It is described in [Poore & Nemecek (2018)](https://science.sciencemag.org/content/360/6392/987).
"""
from hestia_earth.schema import ProductStatsDefinition, TermTermType
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.property import _get_nitrogen_content
from hestia_earth.models.utils.product import _new_product, animal_produced
from hestia_earth.models.utils.input import get_feed_nitrogen
from hestia_earth.models.utils.term import get_excreta_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.animalFeed": "",
        "dataCompleteness.products": "",
        "inputs": [{
            "@type": "Input",
            "term.termType": ["crop", "animalProduct", "other"],
            "optional": {
                "properties": {"@type": "Property", "term.@id": "nitrogenContent"}
            }
        }],
        "products": [{
            "@type": "Product",
            "term.termType": ["liveAnimal", "animalProduct", "liveAquaticSpecies"],
            "optional": {
                "properties": {"@type": "Property", "term.@id": "nitrogenContent"}
            }
        }]
    }
}
RETURNS = {
    "Product": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}


def _product(value: float, excreta: str):
    product = _new_product(excreta, value, MODEL)
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(term_id: str, mass_balance_items: list, alternate_items: list):
    inputs_n, products_n = mass_balance_items
    product_value, nitrogen_content = alternate_items
    value = inputs_n - products_n if all(mass_balance_items) else 3.31 * product_value * nitrogen_content / 100
    return [_product(value, term_id)]


def _no_excreta_term(products: list):
    term_ids = get_excreta_terms()
    return all([not find_term_match(products, term) for term in term_ids])


def _get_excreta_n_term(product: dict):
    return get_lookup_value(product.get('term', {}), 'excreta', model=MODEL)


def _should_run(cycle: dict):
    primary_prod = find_primary_product(cycle) or {}
    excreta = _get_excreta_n_term(primary_prod)
    dc = cycle.get('dataCompleteness', {})
    is_complete = dc.get('animalFeed', False) and dc.get('products', False)
    inputs = cycle.get('inputs', [])
    inputs_n = get_feed_nitrogen(inputs)
    products = cycle.get('products', [])
    products_n = animal_produced(products) / 100
    no_excreta = _no_excreta_term(products)

    # we can still run the model for `liveAquaticSpecies`
    is_liveAquaticSpecies = primary_prod.get('term', {}).get('termType') == TermTermType.LIVEAQUATICSPECIES.value
    product_value = list_sum(primary_prod.get('value', [0]))
    nitrogen_content = _get_nitrogen_content(primary_prod)

    logRequirements(model=MODEL, term=excreta,
                    is_complete=is_complete,
                    inputs_n=inputs_n,
                    products_n=products_n,
                    no_excreta=no_excreta,
                    is_liveAquaticSpecies=is_liveAquaticSpecies,
                    product_value=product_value,
                    nitrogen_content=nitrogen_content)

    mass_balance_items = [inputs_n, products_n]
    alternate_items = [product_value, nitrogen_content]

    should_run = all([
        excreta,
        no_excreta,
        any([
            is_complete and all(mass_balance_items),
            is_liveAquaticSpecies and all(alternate_items)
        ])
    ])
    logShouldRun(MODEL, excreta, should_run)
    return should_run, excreta, mass_balance_items, alternate_items


def run(cycle: dict):
    should_run, excreta, mass_balance_items, alternate_items = _should_run(cycle)
    return _run(excreta, mass_balance_items, alternate_items) if should_run else []
