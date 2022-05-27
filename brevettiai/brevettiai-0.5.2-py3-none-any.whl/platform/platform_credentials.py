import logging

import requests
from dataclasses import dataclass, field
from typing import List

from brevettiai.interfaces.aws import parse_sts_assume_role_response, AWSConfigCredentials
from brevettiai.interfaces.sagemaker import SagemakerCredentials
from brevettiai.io.credentials import Credentials, CredentialsChain, LoginError

log = logging.getLogger(__name__)


class JobCredentials(Credentials):
    """
    Credentials manager for the job context
    """

    def __init__(self, guid=None, apiKey=None, host=None):
        self.host = host
        self.guid = guid
        self.apiKey = apiKey
        self._platform = None

    @property
    def platform(self):
        try:
            from brevettiai.platform import backend, PlatformBackend
            if self._platform is None:
                self.platform = backend
        except ImportError:
            return None
        return self._platform

    @platform.setter
    def platform(self, platform):
        self._platform = platform

    def set_credentials(self, type, user, secret, platform="__keep__", **kwargs):
        """
        Set api credentials to use
        :param type: reacts if type is 'JobCredentials'
        :param user: the job GUID
        :param secret: the job apiKey
        :param platform:
        :return:
        """
        if type == "JobCredentials":
            if platform != "__keep__":
                self.platform = platform
            self.guid = user
            self.apiKey = secret

    def get_sts_access_url(self, resource_id, resource_type, mode):
        """
        get url for requesting sts token
        :param resource_id: id of resource
        :param resource_type: type of resource 'dataset', 'job'
        :param mode: 'read' / 'r', 'write' / 'w'
        :return:
        """
        assert self.guid
        assert self.apiKey

        if mode in {'read', 'r'}:
            if resource_type is "dataset":
                return f"{self.platform.host}/api/data/requests/{self.guid}/?apiKey={self.apiKey}&datasetId={resource_id}"
            elif resource_type is "job":
                return f"{self.platform.host}/api/data/requests/{self.guid}/?apiKey={self.apiKey}&modelId={resource_id}"
        elif mode in {'write', 'w'}:
            if resource_type is "dataset":
                return f"{self.platform.host}/api/models/{self.guid}/securitycredentials?key={self.apiKey}&datasetId={resource_id}"
            elif resource_type is "job":
                return f"{self.platform.host}/api/models/{self.guid}/securitycredentials?key={self.apiKey}&modelId={resource_id}"
        return ""

    def get_sts_credentials(self, resource_id, resource_type, mode):
        url = self.get_sts_access_url(resource_id, resource_type, mode)
        r = requests.get(url, timeout=5)
        return parse_sts_assume_role_response(r.text, self.platform)

    def get_credentials(self, resource_id, resource_type="dataset", mode="r"):
        try:
            return self.get_sts_credentials(resource_id, resource_type=resource_type, mode=mode)
        except Exception as ex:
            raise LoginError(f"Error logging in via Job Credentials for '{self.guid}'") from ex


@dataclass
class DefaultJobCredentialsChain(CredentialsChain):
    """
    Default credentials chain for jobs, using api keys, AWS configuration and then Sagemaker as source of login
    """
    chain: List[Credentials] = field(default_factory=lambda: [
        JobCredentials(),
        AWSConfigCredentials(),
        SagemakerCredentials()
    ])


@dataclass
class PlatformDatasetCredentials(Credentials):
    """
    Credentials manager for platform users
    """
    platform_api: 'PlatformAPI'

    def get_credentials(self, resource_id, resource_type="dataset", mode="r"):
        response = self.platform_api.get_dataset_sts_assume_role_response(resource_id)
        return parse_sts_assume_role_response(response, self.platform_api.backend)

    def set_credentials(self, type, user, secret, **kwargs):
        pass

