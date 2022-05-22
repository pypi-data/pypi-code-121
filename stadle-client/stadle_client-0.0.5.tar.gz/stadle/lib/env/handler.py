import os
import logging
from enum import Enum
from stadle.lib.logging.logger import Logger

"""
STADLE Environemtal Variables

STADLE_MODULE_PATH : refers to the path where STADLE source code is located
STADLE_CONFIG_PATH : refers to the path where STADLE config files are located
"""


class EnvironmentVar(Enum):
    STADLE_MODULE_PATH = "STADLE_MODULE_PATH"
    STADLE_CONFIG_PATH = "STADLE_CONFIG_PATH"
    STADLE_AGENT_CONFIG_PATH = "STADLE_AGENT_CONFIG_PATH"
    STADLE_ADMIN_AGENT_CONFIG_PATH = "STADLE_ADMIN_AGENT_CONFIG_PATH"

    PT_INSTALLED_FLAG = "PT_INSTALLED_FLAG"
    TF_INSTALLED_FLAG = "TF_INSTALLED_FLAG"

# name the logger name as class name
logger = Logger("EnvironmentalHandler").logger


class EnvironmentHandler(object):
    def add_variable(self, name: str, value: str):
        os.environ[name] = value

    def update_variable(self, name: str, value: str):
        cur_value = os.getenv(name)
        if cur_value:
            self.add_variable(name=name, value=value)
            logging.info(f"Updating env : {name} = {value}")
        else:
            self.add_variable(name=name, value=value)

    def get_variable(self, variable_name: str):
        return os.getenv(variable_name)

    @property
    def module_path(self):
        return os.getenv(EnvironmentVar.STADLE_MODULE_PATH.value)

    @property
    def config_path(self):
        return os.getenv(EnvironmentVar.STADLE_CONFIG_PATH.value)

    @property
    def agent_config_path(self):
        return os.getenv(EnvironmentVar.STADLE_AGENT_CONFIG_PATH.value)

    @property
    def admin_agent_config_path(self):
        return os.getenv(EnvironmentVar.STADLE_ADMIN_AGENT_CONFIG_PATH.value)

    @staticmethod
    def pt_installed_flag():
        return (os.getenv(EnvironmentVar.PT_INSTALLED_FLAG.value) == 'True')

    @staticmethod
    def tf_installed_flag():
        return (os.getenv(EnvironmentVar.TF_INSTALLED_FLAG.value) == 'True')
