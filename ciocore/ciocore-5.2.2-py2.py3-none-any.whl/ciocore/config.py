"""
A configuration object implemented as a module-level singleton.

Configuration variables can be shared by importing the module. If there are changes in environment variables or other sources, the config can be refreshed. See [config()](#config)
"""

import logging
import os
import multiprocessing
import base64
import json
import re
from ciocore import loggeria

from ciocore.common import CONDUCTOR_LOGGER_NAME

logger = logging.getLogger(CONDUCTOR_LOGGER_NAME)

#https://stackoverflow.com/a/3809435/179412

URL_REGEX=re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")

__config__ = None

def config(force=False):
    """
    DEPRECATED! Use [get()](#get) instead.

    Instantiate a config object if necessary.

    Keyword Arguments:

    * **`force`** --  Discards any existing config object and instantiate a new one -- Defaults to `False`.

    Returns:

    * [Config()](#Config) object containing a dictionary of configuration variables.
    """

    global __config__
    if force or not __config__:
        __config__ = Config()
    return __config__

def get(force=False):
    """
    Instantiate a config object if necessary and return the dictionary.

    Keyword Arguments:

    * **`force`** -- Discards any existing config object and instantiate a new one -- Defaults to `False`.

    Returns:

    * A dictionary containing configuration.
\
    ???+ example
        ``` python
        from ciocore import config

        print(config.get())

        # Result:
        # {
        #   'thread_count': 16,
        #   'priority': 5,
        #   'md5_caching': True,
        #   'log_level': 'INFO',
        #   'url': 'https://dashboard.conductortech.com',
        #   'auth_url': 'https://dashboard.conductortech.com',
        #   'api_url': 'https://api.conductortech.com', 
        #   'api_key': None
        # }
        ```
    """
    global __config__
    if force or not __config__:
        __config__ = Config()
    return __config__.config

class Config(object):
    def __init__(self):
        """
        Create a configuration dictionary.


        Raises:

        * **`ValueError`** -- Invalid inputs, such as badly formed URLs.
        """

        try:
            default_thread_count = min(multiprocessing.cpu_count() * 2, 16)
        except NotImplementedError:
            default_thread_count = 16

        url = os.environ.get("CONDUCTOR_URL", "https://dashboard.conductortech.com")

        if not URL_REGEX.match(url):
            raise ValueError("CONDUCTOR_URL is not valid '{}'".format(url))
 
        api_url = os.environ.get("CONDUCTOR_API_URL", url.replace("dashboard", "api"))
        if not URL_REGEX.match(api_url):
            raise ValueError("CONDUCTOR_API_URL is not valid '{}'".format(api_url))
 
        falsy = ["false", "no", "off", "0"]

        log_level = os.environ.get("CONDUCTOR_LOG_LEVEL", "INFO")
        if log_level not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
            log_level = "INFO"

        self.config = {
            "thread_count": int(os.environ.get("CONDUCTOR_THREAD_COUNT", default_thread_count)),
            "priority": int(os.environ.get("CONDUCTOR_PRIORITY", 5)),
            "md5_caching": False
            if os.environ.get("CONDUCTOR_MD5_CACHING", "True").lower() in falsy
            else True,
            "log_level": log_level,
            "url": url,
            # Keep "auth_url" for backwwards compatibillity only. 
            # Clients should use "url" moving forward. 
            # Remove "auth_url" on the next major version bump.
            "auth_url": url,
            "api_url": api_url,
            "api_key": self.get_api_key_from_variable() or self.get_api_key_from_file(),
        }

    @staticmethod
    def get_api_key_from_variable():
        """
        Attempt to get an API key from the CONDUCTOR_API_KEY environment variable.

        Raises:

        * **`ValueError`** -- An error occurred while loading the key into JSON.

        Returns:

        * JSON object containing the key - base 64 decoded if necessary.
        """
        api_key = os.environ.get("CONDUCTOR_API_KEY")
        if not api_key:
            return
        logger.info("Attempting to read API key from CONDUCTOR_API_KEY")
        try:
            return json.loads(api_key.replace("\n", "").replace("\r", ""))
        except ValueError:
            try:
                result = base64.b64decode(api_key)
                return Config._to_json(result)
            except BaseException:
                result = base64.b64decode(api_key.encode()).decode("ascii")
                return Config._to_json(result)
        except BaseException:
            message = "An error occurred reading the API key from the CONDUCTOR_API_KEY variable"
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def get_api_key_from_file():
        """
        Attempt to get an API key from the file in the CONDUCTOR_API_KEY_PATH environment variable.

        Raises:

        * **`ValueError`** --  An error occurred while reading or loading the key into JSON.

        Returns:

        * JSON object containing the key - base 64 decoded if necessary.
        """
        api_key_path = os.environ.get("CONDUCTOR_API_KEY_PATH")
        if not api_key_path:
            return
        logger.info("Attempting to read API key from CONDUCTOR_API_KEY_PATH")
        try:
            with open(api_key_path, "r") as fp:
                return Config._to_json(fp.read())
        except BaseException:
            message = "An error occurred reading the API key from the path described in the CONDUCTOR_API_KEY_PATH variable"
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def _to_json(content):
        return json.loads(content.replace("\n", "").replace("\r", ""))
