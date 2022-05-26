"""
it4ifree portal clients config
"""

import ConfigParser
import os
import sys
import re

from .logger import LOGGER

DEFAULT_CONFIG_PATH = '/usr/local/etc/it4i-portal-clients/main.cfg'
LOCAL_CONFIG_PATH = os.path.expanduser('~/.it4ifree')
CONFIG_FILES = '\n'.join((4*' ' + DEFAULT_CONFIG_PATH,
                          4*' ' + LOCAL_CONFIG_PATH))

CONFIG = ConfigParser.ConfigParser()
try:
    FOUND_CONFIGS = CONFIG.read([DEFAULT_CONFIG_PATH, LOCAL_CONFIG_PATH])
except BaseException as err:
    LOGGER.error("%s", err)
    sys.exit(1)

if set(FOUND_CONFIGS) == set():
    LOGGER.error("Tried (in the following order), but no configuration found:\n%s",
                 CONFIG_FILES)
    sys.exit(1)
if DEFAULT_CONFIG_PATH not in FOUND_CONFIGS:
    LOGGER.warning("Default config file %s not found", DEFAULT_CONFIG_PATH)
if LOCAL_CONFIG_PATH not in FOUND_CONFIGS:
    LOGGER.info("Local config file %s not found", LOCAL_CONFIG_PATH)

# mandatory configuration options
API_URL = "https://scs.it4i.cz/api/v1/"
try:
    API_URL = CONFIG.get("main", "api_url")
except BaseException:
    pass
API_URL = re.sub(r'\/$', '', API_URL)

if not API_URL.startswith('https://'):
    LOGGER.error("The API URL is not secured using https://")
    sys.exit(1)

IT4IFREETOKEN = None
try:
    IT4IFREETOKEN = CONFIG.get("main", "it4ifreetoken")
except BaseException:
    pass
