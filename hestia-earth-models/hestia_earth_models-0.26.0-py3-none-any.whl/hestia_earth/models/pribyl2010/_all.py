from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logShouldRun
from . import MODEL
from . import organicCarbonPerKgSoil, organicCarbonPerM3Soil, organicMatterPerKgSoil, organicMatterPerM3Soil

MODELS = [
    organicCarbonPerKgSoil,
    organicCarbonPerM3Soil,
    organicMatterPerKgSoil,
    organicMatterPerM3Soil
]


def _should_run(measurement: dict):
    term_id = measurement.get('term', {}).get('@id')
    model_match = next((model for model in MODELS if model.FROM_TERM_ID == term_id), None)

    should_run = all([model_match])
    if model_match:
        logShouldRun(MODEL, model_match.TERM_ID, should_run)
    return should_run, model_match


def _run(measurement: dict):
    should_run, model = _should_run(measurement)
    return model._measurement(measurement) if should_run else None


def run(site: dict): return non_empty_list(map(_run, site.get('measurements', [])))
