import json
import logging
from copy import deepcopy

import pytest

LOGGER = logging.getLogger(__name__)


@pytest.fixture()
def actual_kafka_results(consume_output):
    LOGGER.info('Preparing actual kafka results...')
    return [{k: v for k, v in message.items() if k in ['key', 'value']} for message in consume_output]


@pytest.fixture()
def expected_kafka_results(map_kafka_expected_output):
    LOGGER.info('Preparing expected kafka results...')
    return [{k: v for k, v in message.items() if k in ['key', 'value']} for message in map_kafka_expected_output]


def remove_fields_from_dict(dict_to_update, fields_to_ignore):
    new_dict = deepcopy(dict_to_update)
    if hasattr(dict_to_update, 'items'):
        for key, value in dict_to_update.items():
            if key in fields_to_ignore:
                new_dict.pop(key)
            if isinstance(value, dict):
                new_value = remove_fields_from_dict(value, fields_to_ignore)
                new_dict[key] = new_value
    return new_dict


@pytest.fixture()
def validate_external_results(map_external_expected_output, map_external_actual_output, request):
    LOGGER.info('Validating external results...')
    try:
        kwargs = {'fields_to_ignore': None}
        kwargs.update(getattr(request, 'param', {}))
        if kwargs['fields_to_ignore']:
            map_external_expected_output = [remove_fields_from_dict(record, kwargs['fields_to_ignore']) for record in map_external_expected_output]
            map_external_actual_output = [remove_fields_from_dict(record, kwargs['fields_to_ignore']) for record in map_external_actual_output]
        for expected in map_external_expected_output:
            assert expected in map_external_actual_output
        LOGGER.info('TEST SUCCESS!')
    except AssertionError:
        LOGGER.info(
            f"TEST FAILURE =(\n\nEXTERNAL EXPECTED=\n{json.dumps(map_external_expected_output, indent=4)}\n\nACTUAL:\n{json.dumps(map_external_actual_output, indent=4)}")
        raise


@pytest.fixture()
def validate_kafka_results(actual_kafka_results, expected_kafka_results, request):
    LOGGER.info('Validating kafka results...')
    try:
        kwargs = {'fields_to_ignore': None}
        kwargs.update(getattr(request, 'param', {}))
        if kwargs['fields_to_ignore']:
            expected_kafka_results = [remove_fields_from_dict(record, kwargs['fields_to_ignore']) for record in expected_kafka_results]
            actual_kafka_results = [remove_fields_from_dict(record, kwargs['fields_to_ignore']) for record in actual_kafka_results]
        for expected in expected_kafka_results:
            assert expected in actual_kafka_results
        LOGGER.info('TEST SUCCESS!')
    except AssertionError:
        LOGGER.info(
            f"TEST FAILURE =(\n\nKAFKA EXPECTED=\n{json.dumps(expected_kafka_results, indent=4)}\n\nKAFKA ACTUAL=\n{json.dumps(actual_kafka_results, indent=4)}")
        raise
