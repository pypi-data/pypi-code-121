import pytest

from click.testing import CliRunner


@pytest.fixture(scope="function")
def runner():
    return CliRunner()


@pytest.fixture(scope="function")
def mocker_patch_provider(mocker):
    from unittest.mock import Mock
    from rebotics_sdk.providers.hawkeye import HawkeyeProvider
    process_role_mock = mocker.patch("rebotics_sdk.cli.utils.process_role")
    process_role_mock.return_value = None
    provider_mock = Mock(spec=HawkeyeProvider)
    mocker.patch('rebotics_sdk.cli.utils.ReboticsCLIContext.provider', new=provider_mock)
    return provider_mock
