"""
Credentials module with base Credentials class and concrete implementations
"""
import base64
import os

CLIENT_ID_ENV_VAR = 'HS_CLIENT_ID'
CLIENT_SECRET_ENV_VAR = 'HS_CLIENT_SECRET'


class CredentialsBase:
    """
    Base class for credentials
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        if type(self) == CredentialsBase:  # pylint: disable=unidiomatic-typecheck
            raise TypeError('CredentialsBase may not be instantiated!')
        self.__client_id = client_id
        self.__client_secret = client_secret

    def decode_client_id(self) -> str:
        """
        Decode client_id
        :return: Decoded client_id
        :rtype: str
        """

        assert self.__client_id, 'client_id is invalid'
        return self._decode_b64_data(self.__client_id)

    def decode_client_secret(self) -> str:
        """
        Decode client_secret
        :return: Decoded client_secret
        :rtype: str
        """
        assert self.__client_secret, 'client_secret is invalid'
        return self.__client_secret

    @classmethod
    def _decode_b64_data(cls, data: str) -> str:
        padded_data = cls._b64_pad(data)
        return base64.b64decode(padded_data).decode('ascii')

    @staticmethod
    def _b64_pad(value: str) -> str:
        remainder = len(value) % 4
        result = value
        if remainder == 2:
            result = f'{value}=='
        elif remainder == 3:
            result = f'{value}='

        return result


class CredentialsProvider(CredentialsBase):
    """
    CredentialsProvider is used for explicitly provide credentials through code.
    """

    def __init__(  # pylint: disable=useless-super-delegation
        self, client_id: str, client_secret: str
    ) -> None:
        super().__init__(client_id, client_secret)


class EnvironmentCredentialsProvider(CredentialsBase):
    """
    EnvironmentCredentialsProvider is used for providing credentials through env vars.
    """

    def __init__(self) -> None:
        client_id = os.getenv(CLIENT_ID_ENV_VAR, '')  # get client_id from env
        client_secret = os.getenv(CLIENT_SECRET_ENV_VAR, '')  # get secret from env
        super().__init__(client_id, client_secret)
