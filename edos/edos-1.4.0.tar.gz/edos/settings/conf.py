import configparser
import logging
import os

import yaml
from appdirs import AppDirs

from ..exceptions import UserReadableException


class LocalConfig(dict):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            raise UserReadableException(
                "Error: DO setup tool is not configured. Run {} first.".format(
                    "do-configure"
                )
            )


def _read_config(config_path):
    conf = configparser.ConfigParser()
    conf.read(config_path)
    conf = LocalConfig((s, dict(conf.items(s))) for s in conf.sections())
    return conf


class Config:
    LOG = logging.getLogger(__name__)

    def __init__(self):
        self.reload()

    def reload(self):
        if os.environ.get("TEST_MODE", False) == "true":
            self.config = {
                "DO": {"token": "test_token"},
                "AWS": {"aws_access_key": "test_key", "aws_secret_key": "test_secret"},
                "SWARMPIT": {"token": "test_token"},
            }
        else:
            self.config = (
                _read_config(self.CONFIG_PATH)
                if os.path.exists(self.CONFIG_PATH)
                else LocalConfig()
            )

        self.DIGITAL_OCEAN_CONFIG = self.config["DO"] if "DO" in self.config else {}
        self.AWS_CONFIG = self.config["AWS"] if "AWS" in self.config else {}
        self.SWARMPIT_CONFIG = (
            self.config["SWARMPIT"] if "SWARMPIT" in self.config else {}
        )

    # Interactive mode
    INTERACTIVE = bool(yaml.full_load(os.getenv("INTERACTIVE", "True")))

    USER_DIR = AppDirs("Endevel", "edos")
    CONFIG_PATH = os.path.join(USER_DIR.user_config_dir, "config.ini")

    AWS_ENDPOINT_URL = "https://fra1.digitaloceanspaces.com"
    AWS_REGION = "fra1"

    DOCKER_MAIN_SWARM_HOSTNAME = "swarm1"
    DOCKER_BASE_URL = f"ssh://{DOCKER_MAIN_SWARM_HOSTNAME}"
