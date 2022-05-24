"""Configuration to be used by the library"""
import json
import os

from ..errors.configuration_exceptions import InvalidConfigurationException

DEFAULT_AUTH_SERVER = 'login.hyperscience.net'
DEFAULT_HS_DOMAIN = 'tpi-dev.hyperscience.net'
DEFAULT_REQUEST_TIMEOUT = 120


class Configuration:
    """Configuration class to be used by the client library"""

    def __init__(
        self,
        hs_domain: str,
        auth_server: str = DEFAULT_AUTH_SERVER,
        request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
    ):
        """
        Constructor for Configuration
        :param hs_domain: hyperscience domain
        :type hs_domain: str
        :param auth_server: authentication server domain
        :type auth_server: str
        :param request_timeout: request timeout (in seconds).  Defaults to 120
        :type request_timeout: int
        """
        self.auth_server = auth_server
        self.hs_domain = hs_domain
        self.request_timeout = request_timeout
        validate(self)

    @property
    def auth_server(self) -> str:
        """
        Authorization server property
        :return: authorization server domain
        :rtype: str
        """
        return self.__auth_server

    @auth_server.setter
    def auth_server(self, value: str) -> None:
        """
        Sets authorization server
        :param value: authorization server domain
        :type value: str
        :return: None
        :rtype: None
        """
        assert value, 'auth_server is invalid!'
        self.__auth_server = value

    @property
    def hs_domain(self) -> str:
        """
        Get hyperscience domain
        :return: hyperscience domain
        :rtype: str
        """
        return self.__hs_domain

    @hs_domain.setter
    def hs_domain(self, value: str) -> None:
        """
        Set hyperscience domain
        :param value: hyperscience domain
        :type value: str
        :return: None
        :rtype: None
        """
        assert value, 'hs_domain is invalid!'
        self.__hs_domain = value

    @property
    def request_timeout(self) -> int:
        """
        Get request timeout
        :return: request timeout
        :rtype: int
        """
        return self.__request_timeout

    @request_timeout.setter
    def request_timeout(self, value: int) -> None:
        """
        Set request timeout
        :param value: request timeout
        :type value: int
        :return: None
        :rtype: None
        """
        assert value, 'request_timeout is invalid!'
        self.__request_timeout = value

    @classmethod
    def from_file(cls, file_path: str) -> 'Configuration':
        """
        Create configuration from file.
        :param file_path: full path to json configuration file
        :type file_path: str
        :return: parsed configuration
        :rtype: Configuration
        """
        with open(file_path, 'r') as file:
            data = file.read().replace(os.linesep, '')
            return cls.from_json_string(data)

    @classmethod
    def from_json_string(cls, data: str) -> 'Configuration':
        """
        Create configuration from string.
        :param data: configuration json string
        :type data: str
        :return: parsed configuration
        :rtype: Configuration
        """
        data_dict = json.loads(data)
        auth_server = data_dict.get('auth_server', DEFAULT_AUTH_SERVER)
        hs_domain = data_dict.get('hs_domain')
        request_timeout = data_dict.get('request_timeout', DEFAULT_REQUEST_TIMEOUT)
        return cls(hs_domain, auth_server, request_timeout)


def validate(configuration: Configuration) -> None:
    """
    Validate configuration
    :param configuration: Configuration to validate
    :type configuration: Configuration
    :return: None
    :rtype: None
    :raises: InvalidConfigurationException if configuration fails validation
    """
    if not configuration.hs_domain:
        raise InvalidConfigurationException(invalid_params=['hs_domain'])

    if configuration.request_timeout < 0:
        raise InvalidConfigurationException(invalid_params=['request_timeout'])
