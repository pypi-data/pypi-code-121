from optparse import Option
from os import supports_effective_ids
import re
from typing import Optional

import abc

from . import LoginID
from .core import LoginIDError

from .managements.user_mgmt import _UserManagement
from .managements.code_mgmt import _CodeManagement
from .managements.cred_mgmt import _CredentialManagement


class LoginIdManagement(_UserManagement, _CodeManagement, _CredentialManagement, LoginID):
    """This server SDK can be used with a management application and requires an API credential to be assigned to that integration. 
    All calls made from this SDK are intended to be backend-to-backend calls, as the operations are sensitive.

    Args:
        client_id (str): Client ID as per the value provided on the dashboard
        private_key (str): Private key of the API credential assigned to the application on the dashboard.
        base_url (str, optional): Base URL where requests should be made (if specifying which environment is being used). Defaults to the LoginID production URL if not given (`None`)

    Example::

        from loginid import LoginIdManagememnt
        lManagement = LoginIdManagement(CLIENT_ID, PRIVATE_KEY)
    """

    def __init__(self, client_id: str, private_key: str, base_url: Optional[str] = None) -> None:
        if not private_key:
            raise LoginIDError(400, "BAD_REQUEST", "Private key is required")

        super().__init__(client_id, private_key, base_url=base_url)

    # User Management
    @abc.abstractmethod
    def get_user(self, username: str) -> str:
        return super().get_user(username)

    @abc.abstractmethod
    def delete_by_username(self, username: str) -> str:
        return super().delete_by_username(username)

    @abc.abstractmethod
    def delete_by_user_id(self, user_id: str) -> dict:
        return super().delete_by_user_id(user_id)

    @abc.abstractmethod
    def activate_user_by_id(self, user_id: str) -> dict:
        return super().activate_user_by_id(user_id)

    @abc.abstractmethod
    def deactivate_user_by_id(self, user_id: str) -> dict:
        return super().deactivate_user_by_id(user_id)

    @abc.abstractmethod
    def add_user_without_credentials(self, username: str) -> dict:
        return super().add_user_without_credentials(username)

    # Code Management
    @abc.abstractmethod
    def generate_code(self, code_type: str, code_purpose: str, isAuthorized: bool, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().generate_code(code_type, code_purpose, isAuthorized, user_id, username)

    @abc.abstractmethod
    def authorize_code(self, code: str, code_type: str, code_purpose: str, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().authorize_code(code, code_type, code_purpose, user_id, username)

    @abc.abstractmethod
    def invalidate_all_codes(self, code_type: str, code_purpose: str, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().invalidate_all_codes(code_type, code_purpose, user_id, username)

    # Credential Management
    @abc.abstractmethod
    def get_credentials(self, status: Optional[str] = None, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().get_credentials(status, user_id, username)

    @abc.abstractmethod
    def rename_credential(self, cred_id: str, updated_name: str, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().rename_credential(cred_id, updated_name, user_id, username)

    @abc.abstractmethod
    def revoke_credential(self, cred_id: str, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().revoke_credential(cred_id, user_id, username)

    @abc.abstractmethod
    def force_fido2_credential_init(self: LoginID, user_id: str,
                                    display_name: Optional[str] = None,
                                    roaming_authenticator: bool = False) -> dict:
        return super().force_fido2_credential_init(user_id, display_name, roaming_authenticator)

    @abc.abstractmethod
    def add_doc_scan_credential_init(self: LoginID,
                                     user_id: Optional[str] = None,
                                     username: Optional[str] = None,
                                     credential_name: Optional[str] = None) -> dict:
        return super().add_doc_scan_credential_init(user_id, username, credential_name)

    @abc.abstractmethod
    def add_doc_scan_credential_complete(self: LoginID, credential_id: str, activate_credential: bool,
                                         user_id: Optional[str] = None, username: Optional[str] = None,
                                         ) -> dict:
        return super().add_doc_scan_credential_complete(credential_id, activate_credential, user_id, username)

    @abc.abstractmethod
    def evaluate_doc_scan_credential(self: LoginID, credential_id: str, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().evaluate_doc_scan_credential(credential_id, user_id, username)

    @abc.abstractmethod
    def generate_recovery_code(self: LoginID, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        return super().generate_recovery_code(user_id, username)

    @abc.abstractmethod
    def add_publickey_credential(self: LoginID, publickey: str, publickey_alg: Optional[str] = "ES256", user_id: Optional[str] = None, username: Optional[str] = None, credential_name: Optional[str] = None) -> dict:
        return super().add_publickey_credential(publickey, publickey_alg, user_id, username, credential_name)
