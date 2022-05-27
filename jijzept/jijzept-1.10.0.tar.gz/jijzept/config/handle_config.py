import os

from pathlib import Path
from typing import Dict, Optional, TypeVar, Union
from urllib.parse import ParseResult, urlparse

import toml

_T0 = TypeVar("_T0")

# DEFAULT SETTING
CONFIG_PATH = str(Path.home()) + "/.jijzept/"
HOST_URL = ""
DEFAULT_CONFIG_FILE = "config.toml"


def create_config(token: str, host_url=HOST_URL, config_path=CONFIG_PATH):
    Path(config_path).mkdir(parents=True, exist_ok=True)

    config_dict = {"default": {"url": host_url, "token": token}}
    # save config file's
    config_path = config_path if config_path[-1] == "/" else config_path + "/"
    config_file_name = config_path + DEFAULT_CONFIG_FILE
    with open(config_file_name, mode="w") as f:
        toml.dump(config_dict, f)

    return config_file_name


def load_config(file_name: str, config="default") -> dict:
    """load config file (TOML file)

    Args:
        file_name (str): path to config file.
        config (str, optional): loading enviroment name. Defaults to 'default'.

    Raises:
        TypeError: if 'config' enviroment is not defined in config file.

    Returns:
        dict: {'token': 'xxxx', 'url': 'xxxx'}
    """
    p_rel = Path(file_name)
    with open(p_rel) as f:
        toml_setting_file = toml.load(f)
    if config not in toml_setting_file:
        raise TypeError(
            "'{}' is not define in config file ({}).".format(config, file_name)
        )
    return toml_setting_file


def _query_and_post_url(url: _T0) -> Dict[str, Union[str, _T0]]:
    parsed = urlparse(url)
    if not parsed.path:
        path = parsed.path + '/query'  
    elif parsed.path[-1] != '/':
        path = parsed.path + '/query'
    else: 
        path = parsed.path + 'query'
    parsed_post_url = ParseResult(
        parsed.scheme,
        parsed.netloc,
        path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ).geturl()
    return {"query_url": url, "post_url": parsed_post_url}


class Config:
    """JijZept API Config

    Attributes:
        query_url (str): Endpoint for Query API.
        post_url (str): Endpoint for Post Instance API.
        token (str): Secret token to connect API.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        proxy: Optional[str] = None,
        config: Optional[str] = None,
        config_env: str = "default",
    ):

        # setting Proxy info
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("'proxy' is `str`.")
            self.proxy = proxy

        if url is not None and token is not None:
            if not isinstance(url, str) or not isinstance(token, str):
                raise TypeError("'url' and 'token' are `str`.")
            endpoints = _query_and_post_url(url)
            self.post_url = endpoints["post_url"]
            self.query_url = endpoints["query_url"]
            self.token = token

        else:
            if config is None:
                config_file = CONFIG_PATH + DEFAULT_CONFIG_FILE
            else:
                config_file = config
            if not os.path.exists(config_file):
                message = "A configuration file does not exist.\n"
                message += "set arguments of __init__(): 'url' and 'token'\n"
                message += "or create config file"
                message += " using `jijzept create` command."
                raise ValueError(message)
            _config = load_config(config_file, config_env)
            self.token = _config[config_env]["token"]

            # Proxy Setup
            if "proxy" in _config[config_env]:
                self.proxy = {
                    "http": _config[config_env]["proxy"],
                    "https": _config[config_env]["proxy"],
                }
            else:
                self.proxy = None

            # If the query_url and post_url are set separately,
            # they will be set as API endpoints in preference to each other.
            query_url = "query_url"
            post_url = "post_url"
            query_url_value = None
            post_url_value = None

            if "url" in _config[config_env]:
                endpoints = _query_and_post_url(_config[config_env]["url"])
                query_url_value = endpoints[query_url]
                post_url_value = endpoints[post_url]
            if query_url in _config[config_env]:
                query_url_value = _config[config_env][query_url]
            if post_url in _config[config_env]:
                post_url_value = _config[config_env][post_url]

            if query_url_value is None or post_url_value is None:
                raise ValueError(
                    "The `url` parameter is required"
                    + " for the K environment in the configuration file."
                )

            self.query_url = query_url_value
            self.post_url = post_url_value
