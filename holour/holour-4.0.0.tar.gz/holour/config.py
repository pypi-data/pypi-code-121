import os
import yaml
import logging


def load_configuration(config_file: str, log: logging.Logger) -> dict:
    config = {}
    if not os.path.exists(config_file):
        log.error(f"The configuration file: {config_file} doesn't exist!")
        return config
    with open(config_file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            log.info(f"Configuration: {config}")
        except yaml.YAMLError as e:
            log.error(e)
    return config
