from __future__ import absolute_import
import re

from rapyuta_io.utils.settings import LABEL_FORMAT
from rapyuta_io.utils.settings import MEASUREMENT_FORMAT
from six.moves import map

label_regex = 'label\.\w+[=]\w+'
# should we change for this: label\.\w+=(true|false) ? Or True|False
measurement_regex = 'measurement\.\w+\.\w+[=><][0-9]+'
# measurement\.\w+\.\w+[=><][-+]?[0-9]*\.?[0-9]+ allows for floats (even written without
# integer part) and negative numbers.
# measurement\.\w+\.\w+([=><]|[><]=)[-+]?[0-9]*\.?[0-9]+ allows for the previous and
# having >= or <=.

__all__ = (
    'build_device_selection_payload',
    'create_label_criteria',
    'create_measurement_criteria'
)


def build_device_selection_payload(query):
    criteria_list = list(map(str.strip, query.split(',')))
    selection_criteria = list()
    for criteria in criteria_list:
        if 'label' in criteria:
            selection_criteria.append(create_label_criteria(criteria))
        else:
            selection_criteria.append(create_measurement_criteria(criteria))
    return {"clause": "AND", "selection_criteria": selection_criteria}


def create_label_criteria(criteria):
    if not bool(re.match(label_regex, criteria)):
        raise ValueError(
            "The query %s does not match the required pattern" % criteria)
    operator = '='
    temp = criteria.split('=')
    key = temp[0].split('.')[1]
    value = temp[1]
    label = LABEL_FORMAT
    label['labels']['select_criteria']['fields'][0]['operator'] = operator
    label['labels']['select_criteria']['fields'][0]['field'] = key
    label['labels']['select_criteria']['fields'][0]['values'][
        'max_value'] = value
    return label


def create_measurement_criteria(criteria):
    if not bool(re.match(measurement_regex, criteria)):
        raise ValueError(
            "The query %s does not match the required pattern" % criteria)
    operator = '>' if '>' in criteria else '<'
    temp = re.split(r'[><]', criteria)
    telemetry = temp[0].split('.')[1]
    field = temp[0].split('.')[2]
    value = temp[1]
    measurement = MEASUREMENT_FORMAT
    measurement['measurements']['measurement'] = telemetry
    measurement['measurements']['select_criteria']['fields'][0][
        'operator'] = operator
    measurement['measurements']['select_criteria']['fields'][0]['field'] = field
    measurement['measurements']['select_criteria']['fields'][0]['values'][
        'max_value'] = value
    return measurement
