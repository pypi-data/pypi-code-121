from enum import Enum


class VaultClientError(Enum):
    CONNECT_ERROR = 'Failed to connect to Vault'
    RESPONSE_ERROR = 'Received invalid response from Vault'


class VaultClientException(Exception):
    def __init__(self, error: VaultClientError):
        self.error = error

    def __str__(self):
        return self.error.value
