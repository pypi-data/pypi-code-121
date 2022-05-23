import json
import os
from typing import List, Optional, Tuple, Union

# The path to where the config file is stored
_config_dir = os.path.expanduser("~/.config/geodesic")
_config_path = os.path.join(_config_dir, "config.json")


def get_config():
    os.makedirs(_config_dir, exist_ok=True)
    return ConfigManager().get_active_config()


def _default_config() -> dict:
    """
    Returns the default configuration file as a dict
    """

    cfg = {
        "clusters": [
            {
                "name": "seerai",
                "host": "https://api.geodesic.seerai.space",
                "oauth2": {
                    "client_id": "RlCTevNLPn0oVzmwLu3R0jCF7tfakpq9",
                    "client_secret": "EY5_-6InmoqYSy1ZEKb7vGiUrCTE1JapTtBncaP_w_0_IhuSilZw1YS6pqoJ0n75",
                    "audience": "https://geodesic.seerai.space",
                    "redirect_uri": "https://seerai.space/authPage",
                    "token_uri": "https://seerai.us.auth0.com/oauth/token",
                    "authorization_uri": "https://seerai.us.auth0.com/authorize"
                }

            },
            {
                "name": "seerai-old",
                "host": "https://geodesic.seerai.space",
                "oauth2": {
                    "client_id": "RlCTevNLPn0oVzmwLu3R0jCF7tfakpq9",
                    "client_secret": "EY5_-6InmoqYSy1ZEKb7vGiUrCTE1JapTtBncaP_w_0_IhuSilZw1YS6pqoJ0n75",
                    "audience": "https://geodesic.seerai.space",
                    "redirect_uri": "https://seerai.space/authPage",
                    "token_uri": "https://seerai.us.auth0.com/oauth/token",
                    "authorization_uri": "https://seerai.us.auth0.com/authorize"
                }

            }
        ],
        "active": "seerai"
    }

    return cfg


def _default_scopes() -> list:
    """
    Returns the default oauth cluster scopes
    """
    return [
        "email",
        "openid",
        "profile",
        "picture",
        "offline_access",
        "geodesic:admin",
        "entanglement:read",
        "entanglement:write",
        "spacetime:read",
        "spacetime:write",
        "tesseract:read",
        "tesseract:write",
        "boson:read",
        "boson:write",
        "krampus:read",
    ]


def _write_default_config():
    os.makedirs(_config_dir, exist_ok=True)

    with open(_config_path, "w") as fp:
        json.dump(_default_config(), fp, indent=4, sort_keys=True)


class ClusterConfig:
    """
    ClusterConfig points the geodesic API at a configured Geodesic cluster.
    """
    def __init__(self, cfg: dict) -> None:
        self.name = cfg['name']
        self.host = cfg['host']
        self.oauth2 = OAuth2Config(cfg['oauth2'])
        self.services = {
            s['name']: ServiceConfig(s) for s in cfg.get('services', [])
        }

    def to_dict(self) -> dict:
        """
        Converts this cluster config into a JSON exportable dictionary as would be listed in
        the "clusters" field of the config object.
        """
        d = dict(
            name=self.name,
            host=self.host,
            oauth2=self.oauth2.to_dict(),
        )
        if len(self.services) > 0:
            d['services'] = [
                s.to_dict() for k, s in self.services.items()
            ]
        return d

    def service_host(self, service: str) -> str:
        """
        Given a service (e.g. tesseract, spacetime, etc) returns the host configured for that service

        Arguments:
            service: the service we want the host for (example: 'spacetime')

        Returns:
            the host for that service

        """
        # Get the default host, trim trailing forward slash if present
        default_host = self.host
        if self.host.endswith('/'):
            default_host = self.host[:-1]

        # Is the service host overridden? If so, return that
        if service in self.services:
            host = self.services[service].host
            if host.endswith('/'):
                host = host[:-1]
            return host
        return f'{default_host}/{service}'


class OAuth2Config:
    """
    Configuration for an OAuth2 Provider.
    """
    def __init__(self, cfg: dict) -> None:
        self.client_id = cfg['client_id']
        self.client_secret = cfg['client_secret']
        self.audience = cfg['audience']
        self.redirect_uri = cfg['redirect_uri']
        self.token_uri = cfg['token_uri']
        self.authorization_uri = cfg['authorization_uri']
        self.scopes = cfg.get('scopes', _default_scopes())

    def to_dict(self) -> dict:
        return dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            audience=self.audience,
            redirect_uri=self.redirect_uri,
            token_uri=self.token_uri,
            authorization_uri=self.authorization_uri,
            scopes=self.scopes
        )


class ServiceConfig:
    """
    ADVANCED/DEV usage

    Individual service level configuration. Used for machine-to-machine comms,
    or to point to replacement services as needed.
    """
    def __init__(self, cfg: dict) -> None:
        self.name = cfg['name']
        self.host = cfg['host']

    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            host=self.host
        )


class ConfigManager:
    """
    Manages the active config. Mostly just used by the CLI, but if you needed to programatically change config,
    that's also an option.
    """
    def __init__(self) -> None:
        self._active_config = None

    def list_configs(self) -> Tuple[List[str], str]:
        """
        Return a list of clusters in this config and the active cluster
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # read the config file
        cfg = {}
        with open(_config_path, 'r') as fp:
            cfg = json.load(fp)

        clusters = []
        for cluster in cfg['clusters']:
            clusters.append(cluster['name'])

        return clusters, cfg['active']

    def get_config(self, name: str) -> ClusterConfig:
        """
        Returns the cluster config for the given name. Useful for when the user needs to hop between
        clusters as runtime, also used internally in the CLI.

        Arguments:
            name: the name of the cluster to get the config for

        Returns:
            the requests cluster config
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # Read and parse
        cfg = {}
        with open(_config_path, 'r') as fp:
            cfg = json.load(fp)

        if name is None:
            name = cfg['active']

        for cluster in cfg['clusters']:
            if cluster['name'] == name:
                return ClusterConfig(cluster)

        raise ValueError(f"cluster config '{name}' not found in the config")

    def get_active_config(self) -> ClusterConfig:
        """
        Gets whichever cluster config is active in the config file

        Returns:
            the active cluster config
        """
        if self._active_config is not None:
            return self._active_config
        self._active_config = self.get_config(name=None)
        return self._active_config

    def set_active_config(
                          self, name: str,
                          add_cluster: Optional[Union[ClusterConfig, dict]] = None,
                          overwrite: bool = False
                          ) -> ClusterConfig:
        """
        Set the active cluster config. This can either be a config that's already in the file or a new one

        Arguments:
            name: the name of the cluster to make active
            add_cluster: a ClusterConfig (or dict) to add. Name in the config must match the name argument
            overwrite: overwrite an existing config, if present

        Returns:
            the new active cluster config
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # read the config file
        cfg = {}

        with open(_config_path, 'r') as fp:
            cfg = json.load(fp)

        # If a config was passed in...
        if add_cluster is not None:
            if isinstance(add_cluster, dict):
                add_cluster = ClusterConfig(add_cluster)
            # Validate if the name matches
            if add_cluster.name != name:
                raise ValueError("provided ClusterConfig's name does not match provided name")

            # Where to add this new config
            clusterIdx = -1
            for i, cluster in enumerate(cfg['clusters']):
                if cluster['name'] == add_cluster.name:
                    if not overwrite:
                        raise ValueError("cluster of this name already exists. Set overwrite"
                                         " to True if you want to overwrite existing config")

                    clusterIdx = i
            # Write in the new config
            if clusterIdx >= 0:
                cfg['clusters'][clusterIdx] = add_cluster.to_dict()
            else:
                cfg['clusters'].append(add_cluster.to_dict())

        else:
            found = False
            for cluster in cfg['clusters']:
                if cluster['name'] == name:
                    found = True
            if not found:
                raise ValueError(f"specified cluster name was not found in your config ({_config_path})")

        # Set this as active
        cfg['active'] = name

        # Save the confg
        with open(_config_path, "w") as fp:
            json.dump(cfg, fp, indent=4, sort_keys=True)

        self.get_active_config()
