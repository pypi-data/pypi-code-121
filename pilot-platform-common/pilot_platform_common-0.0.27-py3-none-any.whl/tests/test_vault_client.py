import pytest
from pytest_httpx import HTTPXMock

from common.vault.vault_client import VaultClient
from common.vault.vault_exception import VaultClientException


class TestVaultClient:
    mock_service = 'https://mock_url'
    mock_crt = ''
    mock_token = 'mock_token'
    client = VaultClient(mock_service, mock_crt, mock_token)

    def test_01_get_from_vault_service_notification(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(url=self.mock_service, json={'data': {'secret_1': 'value_1'}})
        secrets = self.client.get_from_vault('service_notification')
        assert type(secrets) == dict
        assert len(secrets) > 0

    def test_02_get_from_vault_service_kg(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(url=self.mock_service, json={'data': {'secret_1': 'value_1'}})
        secrets = self.client.get_from_vault('service_kg')
        assert type(secrets) == dict
        assert len(secrets) > 0

    def test_03_get_from_vault_connect_error(self):
        with pytest.raises(VaultClientException, match='Failed to connect to Vault'):
            invalid_client = VaultClient('https://vault.com/invalid-url', '', 'mock_token')
            invalid_client.get_from_vault('service_notification')

    def test_04_get_from_vault_response_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(url=self.mock_service, json=['invalid'])
        with pytest.raises(VaultClientException, match='Received invalid response from Vault'):
            self.client.get_from_vault('service_notification')
