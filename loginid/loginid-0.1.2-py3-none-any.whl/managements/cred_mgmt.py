from typing import Optional

from .. import LoginID
from ..core import LoginIDError


class _CredentialManagement():
    """
    Credential management class.
    """

    # Credentials
    def get_credentials(self: LoginID,
                        status: Optional[str] = None,
                        user_id: Optional[str] = None,
                        username: Optional[str] = None) -> dict:
        """Get an exhaustive list of credentials for a given user

        Args:
            status (str, optional): The status of the credentials to get. Defaults to None for credentials with any status.
            user_id (str, optional): User ID of the end user who you would like to get the list of credentials for. Defaults to None.
            username (str, optional): Username of the end user, must be present if `user_id` is not. Defaults to None.

        Returns:
            dict: User's credentials if no error

        Raises:
            LoginIDError: If there is an error
        """
        url = f"/credentials/list"

        payload = {"client_id": self._client_id}
        self._update_payload(payload, user_id, username)

        if status:
            payload["status"] = status

        return self._request('post', url, "credentials.list", payload=payload)

    def rename_credential(self: LoginID,
                          cred_id: str,
                          updated_name: str,
                          user_id: Optional[str] = None,
                          username: Optional[str] = None) -> dict:
        """Rename a credential of a user

        Args:
            cred_id (str): The id of the credential to be renamed.
            updated_name (str): The new name.
            user_id (str, optional): The id of the user to rename the credential for. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not. Defaults to None.

        Returns:
            dict: The renamed credential's detail if no error

        Raises:
            LoginIDError: If there is an error
        """

        url = "/credentials/rename"
        payload = {
            "client_id": self._client_id,
            "credential": {
                "uuid": cred_id,
                "name": updated_name
            }
        }

        self._update_payload(payload, user_id, username)

        return self._request('post', url, "credentials.rename", payload)

    def revoke_credential(self: LoginID,
                          cred_id: str,
                          user_id: Optional[str] = None,
                          username: Optional[str] = None) -> dict:
        """Revoke an existing credential from a user

        Args:
            cred_id (str): The credential id to be revoked
            user_id (str, optional): The user id to extract the credential from. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not. Defaults to None.

        Returns:
            dict: The revoked credential's detail

        Raises:
            LoginIDError: If there is an error
        """

        url = "/credentials/revoke"
        payload = {
            "client_id": self._client_id,
            "credential": {
                "uuid": cred_id
            }
        }
        self._update_payload(payload, user_id, username)

        return self._request('post', url, "credentials.revoke", payload)

    def force_fido2_credential_init(self: LoginID,
                                    user_id: str,
                                    display_name: Optional[str] = None,
                                    roaming_authenticator: bool = False) -> dict:
        """Initialize adding a FIDO2 credential without pre-generated authorization code
        Args:
            user_id (str): ID of the user to add new credential to.
            display_name (str, optional): A human-palatable name for the user account, intended only for display. Defaults to None.
            roaming_authenticator (bool, optional): Whether a security key is allowed. Defaults to False.
        Returns:
            dict: The attestation payload for the credentials if no errors

        Raises:
            LoginIDError: If there is an error
        """
        url = '/credentials/fido2/init/force'

        payload = {
            "client_id": self._client_id,
            "user_id": user_id
        }

        options = {}
        if display_name:
            options['display_name'] = display_name
        if roaming_authenticator:
            options['roaming_authenticator'] = roaming_authenticator
        if options:
            payload['options'] = options

        return self._request('post', url, "credentials.force_add", payload)

    def add_doc_scan_credential_init(self: LoginID,
                                     user_id: Optional[str] = None,
                                     username: Optional[str] = None,
                                     credential_name: Optional[str] = None) -> dict:
        """Initialize the adding of a document scan credential

        Args:
            user_id (str optional): ID of the user to add new credential to. Defaults to None.
            username (str, optional): the username to add new credential to, must be present if `user_id` is not. Defaults to None.
            credential_name (str, optional): the name of the new credential. Defaults to None.

        Returns:
            dict: dictionary of form::

                {
                    'credential_id': 'uuid-string',
                    'iframe_url': 'https://ipsidy.com/url',
                }

        Raises:
            LoginIDError: If there is an error
        """
        url = '/credentials/authid/init'

        payload = {
            "client_id": self._client_id,
            "user_id": user_id,
            "username": username
        }
        self._update_payload(payload, user_id, username)

        if credential_name:
            payload['options'] = {
                "credential_name": credential_name
            }

        return self._request('post', url, "credentials.force_add", payload)

    def add_doc_scan_credential_complete(self: LoginID, credential_id: str, activate_credential: bool,
                                         user_id: Optional[str] = None, username: Optional[str] = None,
                                         ) -> dict:
        """Complete the adding of a document scan credential

        Args:
            credential_id (str): The credential id
            active_credential (bool): Whether to activate the credential
            user_id (str, optional): ID of the user to add new credential to. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not. Defaults to None.

        Returns:
            dict: The Fido2 attestation response for the added credential if no errors

        Raises:
            LoginIDError: If there is an error
        """

        url = '/credentials/authid/complete'
        payload = {
            "client_id": self._client_id,
            "credential_uuid": credential_id,
            "activate_credential": activate_credential,
        }
        self._update_payload(payload, user_id, username)

        response = self._request('post', url, "credentials.force_add", payload)

        if activate_credential:
            token = response.get('jwt', '')
            if not self.verify_token(token):
                raise LoginIDError(401, "invalid_token", "Invalid token")

        return response

    def evaluate_doc_scan_credential(self: LoginID, credential_id: str, user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        """Retrieve document scan and evaluate the credential

        Args:
            credential_id (str): The credential id
            user_id (str, optional): ID of the user to add new credential to. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not. Defaults to None.

        Returns:
            dict: a dictionary::

                {
                    "request_url": "https://example.com/authid/evaluate",
                    "token_type": "Bearer",
                    "auth_token": "auth-token-string"
                }

        Raises:
            LoginIDError: If there is an error
        """

        url = '/credentials/authid/evaluate'
        payload = {
            "client_id": self._client_id,
            "credential_uuid": credential_id,
        }
        self._update_payload(payload, user_id, username)

        return self._request('post', url, "credentials.retrieve_sensitive", payload)

    def generate_recovery_code(self: LoginID,
                               user_id: Optional[str] = None,
                               username: Optional[str] = None) -> dict:
        """Generate a recovery code

        Args:
            user_id (str, optional): the id of the user to add recovery code. Defaults to None.
            username (str, optional): the username of the user to add recovery code, must be present if `user_id` is not. Defaults to None.
        Returns:
            dict: raise a LoginIDError if there is an error, else a dictionary::

                {
                    "code" : "paraphrase recovery code",
                    "created_at": "2022-02-01T21:17:52.184Z"
                }
        """

        url = '/credentials/recovery-code'
        payload = {
            "client_id": self._client_id,
        }
        self._update_payload(payload, user_id, username)

        return self._request('post', url, "credentials.add_recovery", payload)

    def add_publickey_credential(self: LoginID, publickey: str, publickey_alg: Optional[str] = "ES256",
                                 user_id: Optional[str] = None, username: Optional[str] = None,
                                 credential_name: Optional[str] = None) -> dict:
        """Add a public key as a new credential

        Args:
            publickey (str): the public key in PEM format
            user_id (str, optional): the id of the user to add credential. Defaults to None.
            username (str, optional): the username, must be present if `user_id` isn't. Defaults to None.
            credential_name (str, optional): the name of the credential. Defaults to None.

        Returns:
            dict: raise a LoginIDError if there is an error, else a dictionary
        """
        if not (user_id or username):
            raise LoginIDError(400, "bad_request",
                               "`user_id` or `username` must be present")

        url = '/credentials/publickey'
        payload = {
            "client_id": self._client_id,
            "publickey_alg": publickey_alg,
            "publickey": publickey
        }
        self._update_payload(payload, user_id, username)

        if credential_name:
            payload['options'] = {
                "credential_name": credential_name
            }

        return self._request('post', url, "credentials.force_add", payload)
