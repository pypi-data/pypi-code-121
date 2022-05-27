from typing import Optional
from . import _LoginIdClient, LoginIDError


class _Auth:

    ###########################################################################
    #### Registration                                                      ####
    ###########################################################################
    def register_fido2_init(self: _LoginIdClient,
                            username: str,
                            display_name: Optional[str] = None,
                            roaming_authenticator: bool = False) -> dict:
        """
        Initiate a FIDO2 registration

        Args:
            username (str): The username to be registered.
            display_name (str, optional): A human-palatable name for the user account, intended only for display. Defaults to None.
            roaming_authenticator (bool, optional): Whether the authenticator is a security key. Defaults to False.
        Returns:
            dict: The Fido2 attestation payload
        """
        url = "/register/fido2/init"

        payload = dict(
            client_id=self._client_id
        )
        self._update_payload(payload, username=username)

        options = {}
        if display_name:
            options["display_name"] = display_name
        if roaming_authenticator:
            options["roaming_authenticator"] = True
        if options:
            payload["options"] = options

        return self._request('post', url, "auth.register", payload=payload)

    def register_fido2_complete(self: _LoginIdClient, username: str,
                                attestation_payload: dict,
                                credential_name: Optional[str] = None) -> dict:
        """Complete a FIDO2 registration

        Args:
            username (str): The username.
            attestation_payload (dict): the attestation payload.
            credential_name (str, optional): The credential name. Defaults to None.
        """

        url = "/register/fido2/complete"

        payload = dict(
            client_id=self._client_id,
            attestation_payload=attestation_payload,
        )
        self._update_payload(payload, username=username)

        if credential_name:
            payload['options'] = {"credential_name": credential_name}

        auth_response = self._request('post', url, "auth.register", payload)
        token = auth_response.get('jwt', '')
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_token", "Invalid token")

        return auth_response

    def register_password(self: _LoginIdClient, username: str, password: str) -> dict:
        """Register a new user with password

        Args:
            username (str): The username to be registered

        Args:
            username (str): The new username
            password (str): The password

        Returns:
            dict: The registration response
        """
        url = '/register/password'
        payload = {
            "client_id": self._client_id,
            "password": password,
            "password_confirmation": password,
        }
        self._update_payload(payload, username=username)

        auth_response = self._request('post', url, "auth.register", payload)

        token = auth_response.get('jwt', '')
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_token", "Invalid token")

        return auth_response

    ###########################################################################
    #### Authentication                                                    ####
    ###########################################################################
    def authenticate_password(self: _LoginIdClient,
                              username: str,
                              password: str) -> dict:
        """Authenticate user with password

        Args:
            username (str): The username to be authenticated
            password (str): The password

        Returns:
            dict: The authentication response.
        """
        url = f"/authenticate/password"
        payload = {
            "client_id": self._client_id,
            "password": password,
        }
        self._update_payload(payload, username=username)

        response = self._request('post', url, "auth.login", payload=payload)

        token = response.get('jwt', '')
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_token", "Invalid token")

        return response

    # Fido2
    def authenticate_fido2_init(self: _LoginIdClient, username: str) -> dict:
        """Initialize authentication process with a FIDO2 credential

        Args:
            username (str): The username to be authenticated.

        Returns:
            dict: a dictionary::

                {
                    "assertion_payload": {
                        "challenge": "string",
                        "rpId": "string",
                        "allowCredentials": [
                            {
                                "id": "string",
                                "type": "fiod2",
                                transports: ["string"]
                            }
                        ],
                    }
                }

        Raises:
            LoginIDError: If there is an error
        """

        url = '/authenticate/fido2/init'
        payload = {
            "client_id": self._client_id,
        }
        self._update_payload(payload, username=username)

        return self._request('post', url, "auth.login", payload)

    def authenticate_fido2_complete(self: _LoginIdClient, username: str, assertion_payload: dict) -> dict:
        """Complete authentication process with a FIDO2 credential

        Args:
            username (str): The username to be authenicated.
            assertion_payload (str): The FIDO2 assertion payload

        Returns:
            dict: The authentication response
        """
        url = '/authenticate/fido2/complete'
        payload = {
            "client_id": self._client_id,
            "assertion_payload": assertion_payload,
        }
        self._update_payload(payload, username=username)

        response = self._request('post', url, payload=payload)

        token = response.get('jwt', '')
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_token", "Invalid token")

        return response

    # Code
    def authenticate_code_wait(self, username: str, code: str, code_type: str) -> dict:
        """ Wait for a given code

        Args:
            username (str): The username
            code (str): The code associate to the username
            code_type (str): Type of the code

        Returns: response json
        """

        self.validate_code_type(code_type)

        url = f'/authenticate/code/wait'

        payload = {
            "client_id": self._client_id,
            "username": username,
            "authentication_code": {
                "code": code,
                "type": code_type
            }
        }

        json_response = self._request(
            'post', url, token_scope="auth.temporary", payload=payload)

        token = json_response.get('jwt')
        if (token is None) or (not self.verify_token(token)):
            raise LoginIDError(500, "internal_error", "Invalid token")

        return json_response

    def validate_code_type(self, code_type: str) -> None:
        """Check if a code type is valid, raise an error if not

        Args:
            code_type (str): code type

        """
        if code_type not in self.ALLOWED_CODE_TYPES:
            raise LoginIDError(400, 'BAD_REQUEST',
                               f"{code_type} is not a valid code type")

    # document scan
    def authenticate_doc_scan_init(self: _LoginIdClient, username: str, credential_id: Optional[str] = None) -> dict:
        """Initialize authentication process with a document scan

        Args:
            username (str): The username to be authenticated.
            credential_id (str, optional): the credential id to be used in authentication.

        Returns:
            dict: a dictionary::

                {
                    "credential_uuid": "uuid-string",
                    "iframe_url": "https://example.com/authid/authenticate",
                }

        Raises:
            LoginIDError: If there is an error
        """

        url = '/authenticate/authid/init'
        payload = {
            "client_id": self._client_id,
        }
        self._update_payload(payload, username=username)

        if credential_id:
            payload['options'] = {
                'credential_uuid': credential_id
            }

        return self._request('post', url, "auth.login", payload)

    def authenticate_doc_scan_complete(self: _LoginIdClient, username: str, credential_id: str) -> dict:
        """Complete authentication process with a document scan

        Args:
            username (str): The username to be authenticated.
            credential_id (str): The credential id to be used in authentication

        Returns:
            dict: The authentication response upon success.

        Raises:
            LoginIDError: if authentication fails
        """
        url = '/authenticate/authid/complete'
        payload = {
            "client_id": self._client_id,
            "credential_uuid": credential_id,
        }
        self._update_payload(payload, username=username)

        response = self._request('post', url, payload=payload)
        token = response.get('jwt', '')
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_token", "Invalid token")

        return response

    # publickey
    def authenticate_publickey_init(self: _LoginIdClient,
                                    username: str,
                                    publickey: str,
                                    publickey_alg: Optional[str] = "ES256") -> dict:
        """Initialize an authentication with a public key

        Args:
            username (str): the username to be authenticated.
            publickey (str): the public key in PEM format
            pubickey_alg (str, optional): the algorithm of the public key. Defaults to "ES256".

        Returns:
            dict: raise a LoginIDError if there is an error, else a dictionary::

                {
                    "challenge_id": "uuid-string",
                    "server_nonce": "base64url-encoded-string",
                }
        """

        url = '/authenticate/publickey/init'
        payload = {
            "client_id": self._client_id,
            "publickey_alg": publickey_alg,
            "publickey": publickey
        }
        self._update_payload(payload, username=username)

        return self._request('post', url, token_scope="auth.login", payload=payload)

    def authenticate_publickey_complete(self: _LoginIdClient,
                                        username: str,
                                        challenge_id: str,
                                        assertion: str) -> dict:
        """Complete an authentication with a public key

        Args:
            username (str): the username to be authenticated. Defaults to None.
            challenge_id (str): the challenge id
            assertion (str): the assertion in jwt format

        Returns:
            dict: raise a LoginIDError if there is an error, else a dictionary
        """
        url = '/authenticate/publickey/complete'
        payload = {
            "client_id": self._client_id,
            "challenge_id": challenge_id,
            "assertion": assertion,
        }
        self._update_payload(payload, username=username)

        response = self._request('post', url, payload=payload)

        token = response.get('jwt', '')
        if not self.verify_token(token):
            raise LoginIDError(401, "invalid_token", "Invalid token")

        return response
