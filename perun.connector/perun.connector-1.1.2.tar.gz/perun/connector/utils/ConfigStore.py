import yaml
import os


class ConfigStore(object):

    _LDAPC_CFG_FILE = "perun/connector/config_templates/ldap_connector_cfg.yaml"
    _LDAPC_CFG = None

    _OPENAPI_CFG_FILE = "perun/connector/config_templates/openapi_cfg.yaml"
    _OPENAPI_CFG = None

    _ADAPTERS_MANAGER_CFG_FILE = "perun/connector/config_templates/adapters_manager_cfg.yaml"
    _ADAPTERS_MANAGER_CFG = None

    _ATTR_MAP_FILE = "perun/connector/config_templates/attribute_map.yaml"
    _ATTR_MAP = None

    @staticmethod
    def _load_cfg(cfg_file, property_name):
        if not os.path.exists(cfg_file):
            raise Exception("Config: missing config file: ", cfg_file)
        with open(cfg_file, "r") as f:
            setattr(ConfigStore, property_name, yaml.safe_load(f))

    @staticmethod
    def get_ldapc_config():
        if ConfigStore._LDAPC_CFG is None:
            ConfigStore._load_cfg(ConfigStore._LDAPC_CFG_FILE, "_LDAPC_CFG")
        return ConfigStore._LDAPC_CFG

    @staticmethod
    def get_openapi_config():
        if ConfigStore._OPENAPI_CFG is None:
            ConfigStore._load_cfg(
                ConfigStore._OPENAPI_CFG_FILE, "_OPENAPI_CFG"
            )
        return ConfigStore._OPENAPI_CFG

    @staticmethod
    def get_adapters_manager_config():
        if ConfigStore._ADAPTERS_MANAGER_CFG is None:
            ConfigStore._load_cfg(
                ConfigStore._ADAPTERS_MANAGER_CFG_FILE, "_ADAPTERS_MANAGER_CFG"
            )
        return ConfigStore._ADAPTERS_MANAGER_CFG

    @staticmethod
    def get_attribute_map():
        if ConfigStore._ATTR_MAP is None:
            ConfigStore._load_cfg(ConfigStore._ATTR_MAP_FILE, "_ATTR_MAP")
        return ConfigStore._ATTR_MAP
