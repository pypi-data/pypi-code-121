"""local api client used to obtain
IoT service credentials for iot mqtt communication

"""

import os
import logging
import requests

AppConfig = {
    "appId": "",
    "iotEndpoint": "",
    "thingName": "",
    "accountId": "",
    "key": "",
    "cert": "",
    "ca": ""
}

CONFIG_URL = "http://localhost:{}/api/thing"

def get_local_config(port=5000):
    """get thing configuration from local HTTP server
    """
    env_port = os.getenv('PORT')
    if env_port:
        port = env_port
    url = CONFIG_URL.format(port)
    return get_global_config(url)


def get_global_config(url):
    """get thing configuration from url
    """
    try:
        result = requests.get(url)
        result.raise_for_status()
        if result.status_code == 200:
            data = result.json()
            return data
    except requests.HTTPError:
        logging.error("signalsdk: Configuration can not be obtained")
    except AttributeError:
        logging.error("signalsdk: Invalid data from local thing api server.")
    return None
