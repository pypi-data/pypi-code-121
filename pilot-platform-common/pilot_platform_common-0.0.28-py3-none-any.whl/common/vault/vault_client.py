import httpx

from common.vault.vault_exception import VaultClientError
from common.vault.vault_exception import VaultClientException


class VaultClient:
    def __init__(self, vault_service: str, vault_crt: str, vault_token: str):
        self.vault_service = vault_service
        self.vault_crt = vault_crt
        if vault_crt == '':
            self.vault_crt = False
        self.vault_headers = {'X-Vault-Token': vault_token}

    """Get config based on service namespace"""

    def get_from_vault(self, srv_namespace: str) -> dict:
        # fetch Vault stored configurations
        vault_gotten = httpx.get(self.vault_service, verify=self.vault_crt, headers=self.vault_headers)
        if vault_gotten.status_code != 200:
            raise VaultClientException(VaultClientError.CONNECT_ERROR)

        # check Vault response
        vault_gotten_json = vault_gotten.json()
        if 'data' not in vault_gotten_json:
            raise VaultClientException(VaultClientError.RESPONSE_ERROR)

        # -grant access to service "srv_namespace"
        # default return all configurations-
        # since we might use the vault to directly
        # handle the service return. for now I will just return ALL
        vault_data: dict = vault_gotten_json['data']
        # granted = ConfigCenterPolicy.get_granted(srv_namespace)
        # config_return = {}
        # for k, v in vault_data.items():
        #     validate = lambda key, section: section in key
        #     is_granted = any([validate(k, section) for section in granted])
        #     if is_granted:
        #         config_return[k] = v
        # return config_return if granted else vault_data
        return vault_data
