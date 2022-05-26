from __future__ import absolute_import
import base64
import json
import six
from abc import ABCMeta, abstractmethod
import re
import enum

from rapyuta_io.utils import RestClient, InvalidParameterException
from rapyuta_io.utils.object_converter import ObjBase, enum_field
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data

DOCKER_HUB_REGISTRY = 'https://index.docker.io/v1/'

secret_name_regex = re.compile('^[a-z0-9][a-z0-9-]+[a-z0-9]$')


class Secret(ObjBase):
    """
    Secret is a resource that let's the IO Platform access private resources (Git or Docker Repositories) from
    third-party providers.

    :ivar name: Name of the Secret
    :ivar guid: GUID of the Secret
    :ivar secret_type: Type of the Secret
    :ivar created_at: Creation Time of the Secret
    :ivar creator: Create of the Secret
    :param name: Name of the Secret
    :type name: str
    :param secret_config: Secret Configuration
    :type secret_config: Union[:py:class:`~rapyuta_io.clients.secret.SecretConfigSourceSSHAuth`, :py:class:`~rapyuta_io.clients.secret.SecretConfigSourceBasicAuth`, :py:class:`~rapyuta_io.clients.secret.SecretConfigDocker`]
    """
    SECRET_PATH = '/api/secret'

    def __init__(self, name, secret_config):
        self.validate(name, secret_config)
        self.name = name
        self._secret_config = secret_config
        self.secret_type = secret_config.get_type()
        self.guid = None
        self.created_at = None
        self.creator = None

    @staticmethod
    def validate(name, secret_config):
        if not isinstance(name, six.string_types):
            raise InvalidParameterException('name must be a string')
        length = len(name)
        if length < 3 or length > 253:
            raise InvalidParameterException('length of name must be between 3 and 253 characters')
        if not secret_name_regex.match(name):
            raise InvalidParameterException('name must consist of lower case alphanumeric characters or - and must ' +
                                            'start and end with an alphanumeric character')
        if not isinstance(secret_config, _SecretConfigBase):
            raise InvalidParameterException(
                'secret_config must be of type SourceSecretBasicConfig, SourceSecretSSHConfig or DockerSecretConfig')

    def get_deserialize_map(self):
        return {
            'created_at': 'CreatedAt',
            'guid': 'guid',
            'name': 'name',
            'creator': 'creator',
            'project_guid': 'projectGUID',
            'secret_type': enum_field('type', SecretType),
        }

    def get_serialize_map(self):
        return {
            'type': 'secret_type',
            'name': 'name',
            'data': '_secret_config',
        }

    def delete(self):

        """
        Delete the secret using the secret object.

        Following example demonstrates how to delete a secret using secret object:

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> secret = client.get_secret(guid='secret-id')
        >>> secret.delete()

        """

        if not (hasattr(self, '_core_api_host') and hasattr(self, '_auth_token')):
            raise InvalidParameterException('Secret must be created first')
        url = self._core_api_host + self.SECRET_PATH + '/delete'
        headers = create_auth_header(self._auth_token, self._project)
        payload = {'guid': self.guid}
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute(payload)
        get_api_response_data(response, parse_full=True)


class SecretType(str, enum.Enum):
    """
    SecretType is a Enum type defining different types of Secrets possible on the Platform.

    SecretType can be any of the following types \n

    SecretType.DOCKER \n
    SecretType.SOURCE_BASIC_AUTH \n
    SecretType.SOURCE_SSH_AUTH \n
    """

    def __str__(self):
        return str(self.value)

    DOCKER = 'kubernetes.io/dockercfg'
    SOURCE_BASIC_AUTH = 'kubernetes.io/basic-auth'
    SOURCE_SSH_AUTH = 'kubernetes.io/ssh-auth'


class _SecretConfigBase(six.with_metaclass(ABCMeta, ObjBase)):
    """
    SecretConfigBase is an abstract class that implements that defines abstract methods for all types of SecretConfig
    classes.
    """

    @abstractmethod
    def get_type(self):
        pass

    def get_deserialize_map(self):
        pass

    def get_serialize_map(self):
        pass


class SecretConfigSourceSSHAuth(_SecretConfigBase):
    """
    SecretConfigSSHAuth represents Source Secret with SSH Authentication. This type of secrets can be used to access
    private Git repositories using SSH, for building the Docker images from Source Code.

    :param ssh_key: Private SSH key for authenticating with the Git repository hosting
    :type ssh_key: str
    """

    def __init__(self, ssh_key):
        self.validate(ssh_key)
        self.ssh_key = ssh_key

    @staticmethod
    def validate(ssh_key):
        if not (isinstance(ssh_key, str) or isinstance(ssh_key, six.string_types)) or ssh_key == '':
            raise InvalidParameterException('ssh_key cannot be empty')

    @classmethod
    def get_type(cls):
        return SecretType.SOURCE_SSH_AUTH

    def serialize(self):
        return {
            'ssh-privatekey': base64.b64encode(self.ssh_key.encode()).decode()
        }


class SecretConfigSourceBasicAuth(_SecretConfigBase):
    """
    SecretConfigSourceBasicAuth represents Source Secret with Basic Authentication. This type of secrets can be used to
    access private Git repositories exposing HTTP interface, for building the Docker images from Source Code.

    :param username: Username for the Git repository hosting
    :type username: str
    :param password: Password for the Git repository hosting
    :type password: str
    :param ca_cert: If the Git repository is using self-signed certificates, a CA Root Certificate can optionally be provided.
    :type ca_cert: str
    """

    def __init__(self, username, password, ca_cert=None):
        self.validate(username, password, ca_cert)
        self.username = username
        self.password = password
        self.ca_cert = ca_cert

    @staticmethod
    def validate(username, password, ca_cert):
        if not isinstance(username, six.string_types) or username == '':
            raise InvalidParameterException('username cannot be empty')
        if not isinstance(password, six.string_types) or password == '':
            raise InvalidParameterException('password cannot be empty')
        if ca_cert is not None and (not isinstance(ca_cert, six.string_types) or ca_cert == ''):
            raise InvalidParameterException('ca_cert cannot be empty')

    @classmethod
    def get_type(cls):
        return SecretType.SOURCE_BASIC_AUTH

    def serialize(self):
        ret = {
            'username': base64.b64encode(self.username.encode()).decode(),
            'password': base64.b64encode(self.password.encode()).decode(),
        }
        if self.ca_cert is not None:
            ret['ca.crt'] = base64.b64encode(self.ca_cert.encode()).decode()

        return ret


class SecretConfigDocker(_SecretConfigBase):
    """
    SecretConfigDocker represents Docker Secret for Docker registries. This type of secrets can be used to access
    private Docker repositories for either pulling base images or pushing the images from Builds.

    :param username: Username for the Container Registry
    :type username: str
    :param password: Password/Token for the Container Registry
    :type password: str
    :param registry: The URL for the Container Registry, by default it uses DockerHub Registry
    :type registry: str
    """

    def __init__(self, username, password, email, registry=DOCKER_HUB_REGISTRY):
        self.validate(username, password, email, registry)
        self.username = username
        self.password = password
        self.email = email
        self.registry = registry

    @staticmethod
    def validate(username, password, email, registry):
        if not isinstance(username, six.string_types) or username == '':
            raise InvalidParameterException('username cannot be empty')
        if not isinstance(password, six.string_types) or password == '':
            raise InvalidParameterException('password cannot be empty')
        if not isinstance(email, six.string_types) or email == '':
            raise InvalidParameterException('email cannot be empty')
        if not isinstance(registry, six.string_types) or registry == '':
            raise InvalidParameterException('registry cannot be empty')

    @classmethod
    def get_type(cls):
        return SecretType.DOCKER

    def serialize(self):
        config = json.dumps({
            self.registry: {
                'username': self.username,
                'password': self.password,
                'email': self.email,
                'auth': base64.b64encode('{}:{}'.format(self.username, self.password).encode()).decode()
            }
        })
        return {
            '.dockercfg': base64.b64encode(config.encode()).decode()
        }
