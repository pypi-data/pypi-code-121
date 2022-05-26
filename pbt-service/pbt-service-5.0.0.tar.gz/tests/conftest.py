import pytest
from service import Config
from service.fn import setup_logger, is_debug, new_log


def pytest_logger_config(logger_config):
    """Init conf."""
    conf = Config.create()
    setup_logger(config_path=conf.log_config, debug=is_debug())


@pytest.fixture(autouse=True)
def log():
    """Inject logger."""
    return new_log(__name__)
