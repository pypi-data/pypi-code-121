from os import getenv

from service import Config, Env
from service.fn import is_debug, is_testing
from service.i18n import locales


def test_config():
    """Don`t forget populate env variables before run tests."""
    config = Config.create()

    assert config.service_host == getenv('SERVICE_HOST')
    assert config.service_port == int(getenv('SERVICE_PORT'))
    assert config.debug == bool('true' in str(getenv('DEBUG')).lower())

    assert config.testing == is_testing()
    assert config.debug == is_debug()
    assert config.environment == Env(getenv('ENVIRONMENT'))
    assert config.locales == locales

    assert config.log_config.exists()
