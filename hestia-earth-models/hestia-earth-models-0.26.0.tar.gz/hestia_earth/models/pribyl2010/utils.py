from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.utils.measurement import _new_measurement
from . import MODEL


def new_measurement(term_id: str, data: dict):
    measurement = _new_measurement(term_id, MODEL)
    return {**data, **measurement, 'statsDefinition': MeasurementStatsDefinition.MODELLED.value}


def _value_func(data: dict, apply_func, key: str = 'value'):
    values = data.get(key, data.get('value', []))
    return list(map(apply_func, values))
