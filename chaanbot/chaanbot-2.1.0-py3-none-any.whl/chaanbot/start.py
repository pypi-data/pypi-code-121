import asyncio
import configparser
import logging
import os
from time import sleep

import appdirs
import pkg_resources
import requests as requests
from nio import LoginError, AsyncClient

from chaanbot.client import Client
from chaanbot.database import Database
from chaanbot.matrix import Matrix
from chaanbot.module_loader import ModuleLoader
from chaanbot.module_runner import ModuleRunner

logger = logging.getLogger("start")


async def main():
    if "DEBUG" in os.environ:
        logger.info("Running in debug mode")
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    config_path = _get_config_path()
    logger.info("Reading config from {}".format(config_path))
    config = configparser.ConfigParser()
    if config.read(config_path):
        matrix_client = await _connect(config)
        matrix = Matrix(config, matrix_client)
        database = Database(config.get("chaanbot", "sqlite_database_location", fallback=None))
        module_loader = ModuleLoader(config, database, requests)
        module_runner = ModuleRunner(config, matrix, module_loader)
        chaanbot = Client(module_runner, config, matrix)
        await chaanbot.run()
    else:
        logger.error("Could not read config file")


async def _connect(config) -> AsyncClient:
    # Connect to a matrix server
    base_url = config.get("chaanbot", "matrix_server_url")
    password = config.get("chaanbot", "password", fallback=None)
    user_id = config.get("chaanbot", "user_id")
    device_name = config.get("chaanbot", "device_name", fallback=None)
    try:
        logger.info("Connecting to {}".format(base_url))

        client = AsyncClient(base_url, user_id, device_id=device_name)
        login_response = await client.login(password, device_name)
        if type(login_response) == LoginError:
            logger.error("Failed to login: %s", login_response.message)
        logger.info("Connection successful")
        return client
    except Exception as e:
        logger.warning("Connection to {} failed".format(base_url) +
                       " with error message: " + str(e) + ", retrying in 5 seconds...")
        sleep(5)
        await _connect(config)


def _get_config_path() -> str:
    """Read configuration file and return its contents
    """
    cfg_dir = appdirs.user_config_dir('chaanbot')
    if not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir)
    cfg_path = os.path.join(cfg_dir, 'chaanbot.cfg')
    if not os.path.isfile(cfg_path):
        create_user_config(cfg_path)
        raise RuntimeError(
            "Config file was not found. New config file created at {}. Edit and rerun bot.".format(cfg_path))
    return cfg_path


def create_user_config(cfg_path):
    """Create the user's config file
    """
    with open(cfg_path, 'wb') as dest:
        sample_config = pkg_resources.resource_string(__name__, "chaanbot.cfg.sample")
        logger.info(sample_config)
        dest.write(sample_config)


asyncio.get_event_loop().run_until_complete(main())
