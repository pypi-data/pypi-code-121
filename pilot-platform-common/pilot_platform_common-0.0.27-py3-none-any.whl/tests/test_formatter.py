import logging
from logging import LogRecord

import pytest

from common.logger.formatter import CustomJsonFormatter
from common.logger.formatter import get_formatter


@pytest.fixture
def custom_json_formatter():
    yield CustomJsonFormatter()


@pytest.fixture
def record(faker):
    record = LogRecord(faker.slug(), logging.INFO, faker.file_path(), faker.pyint(), faker.text(), (), None)
    record.message = record.getMessage()
    yield record


class TestCustomJsonFormatter:
    def test_get_namespace_returns_namespace_defined_in_environment(self, faker, monkeypatch, custom_json_formatter):
        expected_namespace = faker.slug()
        monkeypatch.setenv('namespace', expected_namespace)

        received_namespace = custom_json_formatter.get_namespace()

        assert expected_namespace == received_namespace

    def test_get_namespace_returns_unknown_for_missing_namespace_variable(self, custom_json_formatter):
        expected_namespace = 'unknown'

        received_namespace = custom_json_formatter.get_namespace()

        assert expected_namespace == received_namespace

    def test_get_namespace_caches_value_after_first_call(self, faker, monkeypatch, custom_json_formatter):
        expected_namespace = faker.slug()
        monkeypatch.setenv('namespace', expected_namespace)
        custom_json_formatter.get_namespace()
        monkeypatch.setenv('namespace', faker.slug())

        received_namespace = custom_json_formatter.get_namespace()

        assert expected_namespace == received_namespace

    def test_add_fields_adds_custom_fields_into_the_log_record(self, custom_json_formatter, record):
        log_record = {}
        expected_log_record = {
            'message': record.message,
            'level': record.levelname,
            'namespace': 'unknown',
            'sub_name': record.name,
        }
        custom_json_formatter.add_fields(log_record, record, {})

        assert expected_log_record == log_record


def test_get_formatter_returns_instance_of_custom_json_formatter():
    formatter = get_formatter()

    assert isinstance(formatter, CustomJsonFormatter) is True
