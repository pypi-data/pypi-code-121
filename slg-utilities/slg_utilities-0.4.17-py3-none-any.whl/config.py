
import configparser
import json
import os
import sys

import slg_utilities.access

CONFIG_FILE = "config.ini"


def get(name):
    """
    Get value of `name` from config prioritized by: runtime, local config, and
    global config. Runtime values are environment variables, local values are
    stored in $HOME/.slgotting/config.json, and global values are stored in
    config.ini in the module installation.
    """
    value = get_runtime_config_value(name)
    if not value:
        value = get_local_config_value(name)
    if not value:
        value = get_global_config_value(name)
    if not value:
        raise ValueError("config value for {} not found".format(name))
    return value

def has_name(name):
    try:
        get(name)
        return True
    except ValueError:
        return False

# Runtime config.
def get_runtime_config_value(name):
    return os.environ.get(name)

def set_runtime_config_value(name, value):
    os.environ[name] = str(value)

# Local config.
def get_local_config_value(name):
    config = read_local_config()
    return config.get(name)

def set_local_config_value(name, value):
    config = read_local_config()
    config[name] = value
    write_local_config(config)

def get_local_config_fpath():
    return os.path.join(os.environ["HOME"], "." + "slgotting", "config.json")

def read_local_config():
    """
    Reads local json config file.
    """
    try:
        config = {}
        config_fpath = get_local_config_fpath()
        if os.path.isfile(config_fpath):
            with open(config_fpath, "r") as fh:
                config = json.load(fh)
        return config
    except Exception as e:
        print("Error reading config. {}".format(str(e)), file=sys.stderr)

def write_local_config(config):
    """
    Writes local json config file.
    """
    try:
        config_fpath = get_local_config_fpath()
        if not os.path.isdir(os.path.dirname(config_fpath)):
            os.makedirs(os.path.dirname(config_fpath))

        with open(config_fpath, "w") as fh:
            json.dump(config, fh, indent=4)
        print("Wrote {}".format(config_fpath))
    except Exception as e:
        print("Error writing config. {}".format(str(e)), file=sys.stderr)

# Global config.
def get_global_config_value(name):
    return read_global_config().get(name)

def get_global_config_fpath():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)

def read_global_config():
    """
    Returns staging or production global config according to the return value
    of slg_utilities.access.is_production().
    """
    config_fpath = get_global_config_fpath()
    config = configparser.ConfigParser()
    config.read(config_fpath)
    return config["PRODUCTION"] if slg_utilities.access.is_production() \
        else config["STAGING"]
