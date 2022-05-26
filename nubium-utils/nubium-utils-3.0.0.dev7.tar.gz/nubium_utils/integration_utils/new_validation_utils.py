"""
Likely the format going forward, but kept separate for compatibility.
Still need to adapt eloqua_utils to use a similar output format as salesforce_utils.
Still need to add/finalize external validation toolset.
"""

import logging
from nubium_utils.dict_manipulator import DictManipulator
import json
import dictdiffer
import pytest

LOGGER = logging.getLogger(__name__)


def remove_nu_null(flat_dict):
    return {k: v for k, v in flat_dict.items() if '--NU--NULL' not in v}


def unflatten(flat_dict):
    return DictManipulator(flat_dict).to_dict()


def fill_schema_dict(flat_dict, empty_schema_dict):
    filled_dict = DictManipulator(empty_schema_dict)
    for k, v in flat_dict.items():
        filled_dict[k] = v
    return filled_dict.to_dict()


def nest_sort(d):
    if isinstance(d, dict):
        keys = sorted(d.keys())
        return {k: nest_sort(d[k]) for k in keys}
    elif isinstance(d, list):
        return [nest_sort(i) for i in d]
    else:
        return d


@pytest.fixture()
def preprocess_external_create_data(external_create_data_csv):
    return [remove_nu_null(rec) for rec in external_create_data_csv]


@pytest.fixture()
def preprocess_external_update_data(external_update_data_csv):
    return [remove_nu_null(rec) for rec in external_update_data_csv]


@pytest.fixture()
def preprocess_external_delete_data(external_delete_data_csv):
    return [remove_nu_null(rec) for rec in external_delete_data_csv]


@pytest.fixture()
def preprocess_kafka_input(kafka_input_csv, kafka_input_schema_dict):
    return [fill_schema_dict(remove_nu_null(rec), kafka_input_schema_dict) for rec in kafka_input_csv]


@pytest.fixture()
def preprocess_external_expected(external_expected_data_csv):
    return [nest_sort(remove_nu_null(rec)) for rec in external_expected_data_csv]


@pytest.fixture()
def preprocess_external_actual(preprocess_external_expected, actual_external_records):
    return [nest_sort({k: v if preprocess_external_expected.get(k) != '--NU--SKIP_VALIDATION' else '--NU--SKIP_VALIDATION'}) for k, v in actual_external_records.items() if k in preprocess_external_expected]


@pytest.fixture()
def preprocess_kafka_expected(kafka_expected_data_csv, kafka_output_schema_dict):
    return [nest_sort(fill_schema_dict(remove_nu_null(rec), kafka_output_schema_dict)) for rec in kafka_expected_data_csv]


@pytest.fixture()
def preprocess_kafka_actual(kafka_expected_data_csv, consume_output):
    preprocessed_actual = []
    for idx, record in enumerate([remove_nu_null(rec) for rec in kafka_expected_data_csv]):
        actual = DictManipulator(consume_output[idx])
        for dotkeys, val in record.items():
            if val == '--NU--SKIP_VALIDATION':
                actual['value'][dotkeys] = val
        preprocessed_actual.append(nest_sort(actual.to_dict()))
    return preprocessed_actual


@pytest.fixture()
def validate_kafka_results(format_kafka_expected, format_kafka_actual):
    LOGGER.info('Validating kafka results...')
    failed = False
    for i in range(len(format_kafka_expected)):
        expected = format_kafka_expected[i]
        actual = format_kafka_actual[i]
        try:
            assert expected == actual
        except AssertionError:
            LOGGER.info(
                f"\nKAFKA TEST CASE {i} FAILURE;\nEXPECTED VS ACTUAL DIFFS=\n\n{json.dumps(list(dictdiffer.diff(expected, actual)), indent=4)}\n\nEXPECTED=\n{json.dumps(expected, indent=4)}\n\nACTUAL=\n{json.dumps(actual, indent=4)}\n\n\n")
            failed = True
    if failed:
        raise Exception('TEST FAILED')
    else:
        LOGGER.info('TEST WAS SUCCESSFUL!!')
