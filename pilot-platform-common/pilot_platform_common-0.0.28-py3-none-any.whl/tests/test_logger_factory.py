from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest

from common.logger.logger_factory import LoggerFactory


@pytest.fixture
def logger_factory(faker, tmpdir):
    yield LoggerFactory(faker.slug(), logs_path=tmpdir)


class TestLoggerFactory:
    def test_logger_factory_creates_logs_folder_in_working_directory(self, monkeypatch, faker, tmpdir):
        folder = tmpdir.mkdtemp()
        monkeypatch.chdir(folder)
        expected_folder = folder / 'logs'

        LoggerFactory(faker.slug())

        assert Path(expected_folder).is_dir() is True

    def test_get_logger_returns_logger_with_expected_list_of_handlers(self, logger_factory):
        logger = logger_factory.get_logger()

        expected_handlers = [
            TimedRotatingFileHandler,
            StreamHandler,
            StreamHandler,
        ]

        for idx, expected_handler in enumerate(expected_handlers):
            assert isinstance(logger.handlers[idx], expected_handler) is True
