from optparse import Option
from typing import Optional
from . import _LoginIdClient, LoginIDError


class _Credentials:
    def init_add_fido2_credential_with_code(self: _LoginIdClient,
                                            code: str, code_type: str, username: str,
                                            display_name: Optional[str] = None,
                                            roaming_authenticator: bool = False) -> dict:
        """initialize adding a FIDO2 credential with pre-authorized code

        Args:
            code (str): The authorization code
            code_type (str): The code type, must be listed in `ALLOWED_CODE_TYPES`
            username (str): The username to add the new credential.
            display_name (str, optional): A human-palatable name for the user account, intended only for display. Defaults to None.
            roaming_authenticator (bool, optional): Whether the credential is a security key. Defaults to False.

        Returns:
            dict: the FIDO2 attestation payload.
        """
        url = '/credentials/fido2/init/code'

        payload = {
            "client_id": self._client_id,
            "authentication_code": {
                "code": code,
                "type": code_type
            },
        }

        options = {}
        if display_name:
            options["display_name"] = display_name
        if roaming_authenticator:
            options["roaming_authenticator"] = True
        if options:
            payload["options"] = options

        self._update_payload(payload, username=username)

        return self._request('post', url, "credentials.add", payload)

    def complete_add_fido2_credential(self: _LoginIdClient, attestation_payload: dict,
                                      username: str, credential_name: Optional[str] = None) -> dict:
        """Complete adding a FIDO2 credential (initialized with or without code)

        Args:
            attestation_payload (dict): The attestation payload returned by init functions
            username (str): The username to add the new credential.
            credential_name (str, optional): The name of the new credential. Defaults to None.

        Returns:
            dict: The attestation payload for the credentials if no errors

        Raises:
            LoginIDError: If there is an error
        """
        url = '/credentials/fido2/complete'

        payload = {
            "client_id": self._client_id,
            "attestation_payload": attestation_payload
        }
        self._update_payload(payload, username=username)

        if credential_name:
            payload["options"] = {
                "credential_name": credential_name
            }

        attestation_response = self._request(
            'post', url, payload=payload)

        # validate the jwt
        token = attestation_response.get("jwt", "")
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_jwt", "Invalid JWT")

        return attestation_response
