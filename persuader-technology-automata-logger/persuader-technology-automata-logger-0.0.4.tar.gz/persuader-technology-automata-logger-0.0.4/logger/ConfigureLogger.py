import importlib.resources as package_resources
import logging.config

import yaml

from logger import conf


class ConfigureLogger:

    def __init__(self, config='default-log-config.yaml', log_level=None):
        if log_level is not None:
            logging.basicConfig(level=log_level)
        else:
            self.load_yaml_log_config(config)

    def load_yaml_log_config(self, config):
        config_content = self.get_log_config_file_contents(config)
        logging_config = yaml.safe_load(config_content)
        logging.config.dictConfig(logging_config)

    @staticmethod
    def get_log_config_file_contents(config):
        return package_resources.read_text(conf, config)
