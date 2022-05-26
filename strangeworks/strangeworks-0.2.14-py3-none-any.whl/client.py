import os, yaml
from strangeworks.backend.backends import BackendService

from strangeworks.circuit_runner.circuit_runner import CircuitRunner
from strangeworks.jobs.jobs import Job
from strangeworks.rest_client.rest_client import StrangeworksRestClient

import importlib.metadata

__version__ = importlib.metadata.version("strangeworks")


class Client(object):
    """Strangeworks client implements the Strangeworks API and provides core functionality for cross-vendor applications"""

    def __init__(
        self,
        username: str = None,  # the unique username found on quantumcomputing.com
        api_key: str = None,  # a secret api_key that can be accessed on quantumcomputing.com
        auth_token: str = None,  # a jwt token used for authorization.
        host: str = None,  # the host URL. defaults to https://api.quantumcomputing.com
        config_location: str = None,  # the config location to the SDK configuration. can ge generated using the Strangeworks CLI
        auth_location: str = None,  # the location of the authentication configuration. can be generated using the Strangeworks CLI
        project_id: str = None,  # the project ID to utilize for this session.
        result_id: str = None,  # the result ID to append result data to in this session
        headers: dict = None,  # headers that are sent as part of the request to Strangeworks
        rest_client: StrangeworksRestClient = None,
    ):
        """
        Client configuration is heirchical and flows as follows:
        - Configuration file
        - Environment variables
        - __init__ parameters
        """

        # set each parameter utilizing the parameter passed into the init function
        # or the environment variable in that order of preference
        self.__username = (
            os.getenv("STRANGEWORKS_USERNAME", default=None)
            if username is None
            else username
        )

        self.__api_key = (
            os.getenv("STRANGEWORKS_API_KEY", default=None)
            if api_key is None
            else api_key
        )

        self.__auth_token = (
            os.getenv("STRANGEWORKS_AUTH_TOKEN", default=None)
            if auth_token is None
            else auth_token
        )

        self.__host = (
            os.getenv("STRANGEWORKS_HOST", default=None) if host is None else host
        )

        self.__config_location = (
            os.getenv("STRANGEWORKS_CONFIG_LOCATION", default=None)
            if config_location is None
            else config_location
        )

        self.__auth_location = (
            os.getenv("STRANGEWORKS_AUTH_LOCATION", default=None)
            if auth_location is None
            else auth_location
        )

        self.__project_id = (
            os.getenv("STRANGEWORKS_PROJECT_ID", default=None)
            if project_id is None
            else project_id
        )

        self.headers = (
            os.getenv("STRANGEWORKS_HEADERS", default=None)
            if headers is None
            else headers
        )

        self.result_id = (
            os.getenv("STRANGEWORKS_RESULT_ID", default=None)
            if result_id is None
            else result_id
        )

        # set the default config location if none was set
        if self.__config_location is None:
            strange_config_directory = os.path.expanduser("~/.config/strangeworks")
            default_strange_config_file_path = f"{strange_config_directory}/config.yaml"
            if os.path.isfile(default_strange_config_file_path):
                self.config_location = default_strange_config_file_path

            # do the same for auth file ...
            auth_file_path = f"{strange_config_directory}/auth.yaml"
            if os.path.isfile(auth_file_path):
                self.__auth_location = auth_file_path

        # if a file was set load the client up utilizing the configuration file
        if self.__config_location is not None:
            with open(self.__config_location, "r") as conf_file:
                cfg = yaml.safe_load(conf_file)

            self.__project_id = (
                cfg.get("project_id", None)
                if self.__project_id is None
                else self.__project_id
            )

            self.headers = (
                cfg.get("headers", None) if self.headers is None else self.headers
            )
            self.__host = cfg.get("host", None) if self.__host is None else self.__host

        # set up auth config from auth.yaml if it exists. will only
        # set value if its currently set to None
        if self.__auth_location is not None:
            with open(self.__auth_location, "r") as auth_file:
                auth_cfg = yaml.safe_load(auth_file)

            self.__api_key = (
                auth_cfg.get("sdk_key", None) if api_key is None else api_key
            )

            self.__auth_token = (
                auth_cfg.get("sdk_token", None) if auth_token is None else auth_token
            )

            self.__username = (
                auth_cfg.get("username", None) if username is None else username
            )

        if rest_client is not None:
            self.rest_client = rest_client
        else:
            self.rest_client = StrangeworksRestClient(
                headers=headers,
                host=self.__host,
                username=self.__username,
                api_key=self.__api_key,
                auth_token=self.__auth_token,
                version=__version__,
            )

        self.backends_service = BackendService(self.rest_client)

        self.circuit_runner = CircuitRunner(
            rest_client=self.rest_client, result_id=self.result_id
        )

    def authenticate(self, username: str = None, api_key: str = None):
        """
        authenticate is used to generate an auth token and utilized within the session
        with the username and api_key. Will overwrite an auth token that is stored
        either in configuration or memory when called
        """
        self.__username = username
        self.__api_key = api_key
        self.rest_client.authenticate(username=username, api_key=api_key)
        self.backends_service._new_client(self.rest_client)
        self.circuit_runner._new_client(self.rest_client)

    def store_configuration(
        self,
        config_path: str = None,
        store_auth: bool = True,
        store_config: bool = True,
    ):
        """
        store_configuration stores the current configuration for the app in the configuration files auth.yaml and
        config.yaml specified by either the config_path or the default configuration directory
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.config/strangeworks")
        if store_auth:
            with open(f"{config_path}/auth.yaml", "w") as authfile:
                yaml.dump(
                    {
                        "api_key": self.__api_key,
                        "auth_token": self.__auth_token,
                        "username": self.__username,
                    },
                    authfile,
                )
        if store_config:
            with open(f"{config_path}/config.yaml", "w") as conffile:
                yaml.dump(
                    {
                        "project_id": self.__project_id,
                        "host": self.__host,
                    },
                    conffile,
                )

    def fetch_job(self, job_id: str) -> Job:
        response = self.rest_client.get(f"/jobs/{job_id}?include=result_data")
        return Job.from_json(job=response, backend=None, rest_client=self.rest_client)

    def _host(self, new_host: str = None):
        self.__host = new_host
        rc = StrangeworksRestClient(
            headers=self.headers,
            host=new_host,
            username=self.__username,
            api_key=self.__api_key,
            auth_token=self.__auth_token,
        )
        self.rest_client = rc
        self.backends_service._new_client(self.rest_client)
        self.circuit_runner._new_client(self.rest_client)
