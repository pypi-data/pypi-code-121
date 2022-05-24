import os
from os.path import expanduser

from jproperties import Properties


class ConfigUtils:
    TOKEN_KEY = "token"
    INTERACTIVE_LOGGING = "progress.logging.console"
    _props = Properties()

    @staticmethod
    def collect_properties():
        file = ConfigUtils.get_properties_path()
        if not os.path.isfile(file):
            open(file, "a").close()
        with open(file, "rb") as f:
            ConfigUtils._props.load(f, "utf-8")
        return ConfigUtils._props

    @staticmethod
    def store_properties(props):
        with open(ConfigUtils.get_properties_path(), "wb") as f:
            props.store(f, encoding="utf-8")

    @staticmethod
    def delete_property(props, key):
        del props[key]
        ConfigUtils.store_properties(props)

    @staticmethod
    def store_property(props, key, value):
        props[key] = value
        ConfigUtils.store_properties(props)

    @staticmethod
    def set_property(props, key, value):
        props[key] = value
        ConfigUtils.store_properties(props)

    @staticmethod
    def get_property(key):
        return ConfigUtils._props[key].data

    @staticmethod
    def store_token(props, token):
        ConfigUtils.store_property(props, ConfigUtils.TOKEN_KEY, token)

    @staticmethod
    def get_token(props):
        return props[ConfigUtils.TOKEN_KEY].data

    @staticmethod
    def is_interactive_print_enabled():
        return (
            ConfigUtils._props.get(ConfigUtils.INTERACTIVE_LOGGING) is None
            or ConfigUtils._props[ConfigUtils.INTERACTIVE_LOGGING].data.lower()
            == "true"
        )

    @staticmethod
    def get_properties_path():
        if os.environ.get("FEATURESTORE_USER_CONFIG") is not None:
            return os.environ.get("FEATURESTORE_USER_CONFIG")
        else:
            return expanduser("~") + os.path.sep + ".featurestore.config"
