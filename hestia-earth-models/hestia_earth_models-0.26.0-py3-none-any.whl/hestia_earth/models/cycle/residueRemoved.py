from hestia_earth.schema import TermTermType, PracticeStatsDefinition
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.products": "True",
        "dataCompleteness.cropResidue": "False",
        "products": [{"@type": "Product", "term.termType": "crop"}]
    }
}
RETURNS = {
    "Practice": [{
        "value": "0",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "crop": "isAboveGroundCropResidueRemoved"
}
TERM_ID = 'residueRemoved'


def _practice():
    practice = _new_practice(TERM_ID)
    practice['value'] = [0]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def _is_residue_removed(product: dict):
    return get_lookup_value(product.get('term', {}), 'isAboveGroundCropResidueRemoved', model=MODEL, term=TERM_ID)


def _should_run(cycle: dict):
    products_complete = cycle.get('dataCompleteness', {}).get('products', False)
    crop_residue_incomplete = _is_term_type_incomplete(cycle, {'termType': TermTermType.CROPRESIDUE.value})
    crops = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    removed_crops = list(filter(_is_residue_removed, crops))
    no_residue_removed_crops = len(removed_crops) == 0

    logRequirements(model=MODEL, term=TERM_ID,
                    products_complete=products_complete,
                    crop_residue_incomplete=crop_residue_incomplete,
                    no_residue_removed_crops=no_residue_removed_crops)

    should_run = all([products_complete, crop_residue_incomplete, no_residue_removed_crops])
    logShouldRun(MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return [_practice()] if _should_run(cycle) else []
