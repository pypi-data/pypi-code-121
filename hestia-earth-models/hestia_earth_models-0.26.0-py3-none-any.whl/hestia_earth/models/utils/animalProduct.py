from hestia_earth.schema import TermTermType

from .term import get_lookup_value

FAO_LOOKUP_COLUMN = 'animalProductGroupingFAO'
FAO_EQUIVALENT_LOOKUP_COLUMN = 'animalProductGroupingFAOEquivalent'


def get_animalProduct_lookup_value(model: str, term_id: str, column: str):
    return get_lookup_value({'@id': term_id, 'termType': TermTermType.ANIMALPRODUCT.value}, column,
                            model=model, term=term_id)


def get_animalProduct_grouping_fao(model: str, term: dict):
    fao_product_id = get_animalProduct_lookup_value(model, term.get('@id'), FAO_EQUIVALENT_LOOKUP_COLUMN)
    return get_animalProduct_lookup_value(model, fao_product_id, FAO_LOOKUP_COLUMN)
