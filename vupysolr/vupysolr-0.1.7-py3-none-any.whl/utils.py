import json
import logging
import requests

from . import __version__


def get_logger(name, loglevel=logging.WARNING):
    logger = logging.getLogger(name)
    if not logger.handlers:
        stream = logging.StreamHandler()
        stream.setLevel(loglevel)
        stream.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(stream)
    if logger.level != loglevel:
        logger.setLevel(loglevel)
    return logger


def json_req(url):
    logger = get_logger("vupysolr")
    try:
        response = requests.get(url, headers={"User-Agent": "vupysolr {0}".format(__version__)})
    except requests.exceptions.RequestException as err:
        logger.error(err.__class__.__name__)
        return None
    if response.status_code != 200:
        logger.error("HTTP request to {0} failed!".format(url))
        logger.error("HTTP response code is {0}.".format(response.status_code))
        return None
    if response.text:
        try:
            return json.loads(response.text)
        except json.decoder.JSONDecodeError:
            logger.error("Parsing JSON data retrieved from {0} failed!".format(url))
            return None
