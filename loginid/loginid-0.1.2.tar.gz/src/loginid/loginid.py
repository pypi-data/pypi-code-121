import jwt
from .core import LoginIDError, _LoginIdClient, _Auth, _Credentials

import abc
import base64
import hashlib

from typing import Optional


class LoginID(_Auth, _Credentials, _LoginIdClient):
    """ This server SDK leverages either a web or mobile application
    and requires an API credential to be assigned to that integration.

    Args:
        client_id (str): Client ID as per the value provided on the dashboard
        private_key (str, optional): Private key of the API credential if one is assigned to the application on the dashboard.
        base_url (str, optional): Base URL where requests should be made (if specifying which environment is being used). Defaults to the LoginID production URL if not given (`None`)

    Example::

        from loginid import LoginID
        lid = LoginID(CLIENT_ID, PRIVATE_KEY)
    """
    ###########################################################################
    # Core client APIs
    ###########################################################################
    @abc.abstractmethod
    def generate_service_token(self, scope: str, username: Optional[str] = None, user_id: Optional[str] = None, algo: Optional[str] = None, nonce: Optional[str] = None) -> str:
        return super().generate_service_token(scope, username, user_id, algo, nonce)

    @abc.abstractmethod
    def verify_token(self, token: str, username: Optional[str] = None) -> bool:
        return super().verify_token(token, username)

    @abc.abstractmethod
    def client_id(self) -> str:
        return super().client_id()

    ###########################################################################
    # Transaction APIs
    ###########################################################################
    def generate_tx_auth_token(self, tx_payload: str,
                               nonce: Optional[str] = None,
                               algo: Optional[str] = None) -> str:
        """Generate an Authorization Token for Transaction Flow

        Args:
            tx_payload (str): The transaction payload
            nonce (str, optional): optional nonce for the token, auto-generated if not given
            algo (str, optional): Encryption algorithm, defaults to `"ES256"`

        Returns:
            str: The JWT authorization token
        """

        algo = algo or self.DEFAULT_JWT_ALOGORITHM
        if algo not in self.SUPPORTED_JWT_ALGORITHMS:
            raise LoginIDError(400, "invalid_algorithm", f"{algo} is not an allowed algorithm.")

        # hash and encode tx_payload
        payload_hash = hashlib.sha256(tx_payload.encode()).digest()
        payload_hash = (base64.urlsafe_b64encode(payload_hash)
                              .decode().strip('=')
                        )

        payload = {
            'scope': 'tx.create',
            'nonce': nonce or self._random_string(16),
            'payload_hash': payload_hash,
            'iat': self._get_utc_epoch()
        }

        return jwt.encode(
            payload, self._private_key,
            algorithm=algo,
            headers={'alg': algo, 'typ': 'JWT'}
        )

    def create_tx(self, tx_payload: str, nonce: str = None) -> str:
        """Create a transaction and return its ID

        Args:
            tx_payload (str): The transaction payload
            nonce (str, optional): The optional nonce, randomly generated if not provided

        Returns:
            str: The transaction id if no error
        """

        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.generate_tx_auth_token(tx_payload)
        }
        payload = dict(
            client_id=self._client_id,
            tx_payload=tx_payload,
            nonce=nonce or self._random_string()
        )

        return self._request('post', "/tx", payload=payload, headers=headers)['id']

    def verify_transaction(self, tx_token: str, tx_payload: str) -> bool:
        """Verify the jwt token returned upon completion of a transaction

        Args:
            tx_token (str): The JWT token
            tx_payload (str): the original transaction payload

        Returns: `True` if the token is valid, `False` if not
        """
        headers = jwt.get_unverified_header(tx_token)
        algo, kid = headers.get('alg'), headers.get('kid', '')
        if algo not in self.SUPPORTED_JWT_ALGORITHMS:
            raise ValueError(f"{algo} is not an allowed algorithm")

        # get public key
        public_key = self._get_public_key(kid)

        payload = jwt.decode(tx_token, public_key, algorithms=algo,
                             audience=self._client_id)

        to_hash = "".join([
            tx_payload,
            payload.get("nonce", ""),
            payload.get("server_nonce", "")
        ])
        hash = hashlib.sha256(to_hash.encode()).digest()
        hash = base64.urlsafe_b64encode(hash).decode().strip('=')

        return payload.get('tx_hash') == hash

    ###########################################################################
    # Auth APIs
    ###########################################################################
    # Fifo2
    @abc.abstractmethod
    def register_fido2_init(self, username: str,
                            display_name: Optional[str] = None,
                            roaming_authenticator: bool = False) -> dict:
        return super().register_fido2_init(username, display_name, roaming_authenticator)

    @abc.abstractmethod
    def register_fido2_complete(self, username: str, attestation_payload: str,
                                credential_name: Optional[str] = None) -> dict:
        return super().register_fido2_complete(username, attestation_payload, credential_name)

    @abc.abstractmethod
    def authenticate_fido2_init(self, username: str) -> dict:
        return super().authenticate_fido2_init(username)

    @abc.abstractmethod
    def authenticate_fido2_complete(self, username: str, assertion_payload: str) -> dict:
        return super().authenticate_fido2_complete(username, assertion_payload)

    # password
    @abc.abstractmethod
    def register_password(self, username: str, password: str) -> dict:
        return super().register_password(username, password)

    @abc.abstractmethod
    def authenticate_password(self, username: str, password: str) -> dict:
        return super().authenticate_password(username, password)

    # document scan
    @abc.abstractmethod
    def authenticate_doc_scan_init(self, username: str, credential_id: Optional[str] = None) -> dict:
        return super().authenticate_doc_scan_init(username, credential_id)

    @abc.abstractmethod
    def authenticate_doc_scan_complete(self, username: str, credential_id: str) -> dict:
        return super().authenticate_doc_scan_complete(username, credential_id)

    # publickey
    @abc.abstractmethod
    def authenticate_publickey_init(self, username: str, publickey: str, publickey_alg: Optional[str] = "ES256") -> dict:
        return super().authenticate_publickey_init(username, publickey, publickey_alg)

    @abc.abstractmethod
    def authenticate_publickey_complete(self, username: str, challenge_id: str, assertion: str) -> dict:
        return super().authenticate_publickey_complete(username, challenge_id, assertion)

    ###########################################################################
    # Credentials APIs
    ###########################################################################
    @abc.abstractmethod
    def init_add_fido2_credential_with_code(self: _LoginIdClient, code: str,
                                            codeType: str, username: str,
                                            display_name: Optional[str] = None,
                                            roaming_authenticator: bool = False) -> dict:
        return super().init_add_fido2_credential_with_code(code, codeType, username, display_name, roaming_authenticator)

    @abc.abstractmethod
    def complete_add_fido2_credential(self: _LoginIdClient,
                                      attestation_payload: dict,
                                      username: str,
                                      credential_name: Optional[str] = None) -> dict:
        return super().complete_add_fido2_credential(attestation_payload, username, credential_name)
