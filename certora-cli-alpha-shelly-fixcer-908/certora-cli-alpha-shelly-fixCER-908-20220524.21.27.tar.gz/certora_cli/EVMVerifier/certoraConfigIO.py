from Shared.certoraUtils import Mode, safe_create_dir
import argparse
import json
from datetime import datetime
from copy import deepcopy
from typing import Dict, Any
import logging
from pathlib import Path

"""
This file is responsible for reading and writing configuration files.
"""

# logger for issues regarding the general run flow.
# Also serves as the default logger for errors originating from unexpected places.
run_logger = logging.getLogger("run")


def current_conf_to_file(parsed_options: argparse.Namespace) -> Dict[str, Any]:
    """
    Saves current command line options to a configuration file
    @param parsed_options: command line options after argparse parsing
    @:return the data that was written to the file (in json/dictionary form)
    """
    json_rep = deepcopy(parsed_options.__dict__)

    """
    We are not saving options if they were not provided (and have a simple default that cannot change between runs).
    Why?
    1. The .conf file is shorter
    2. The .conf file is much easier to read, easy to find relevant arguments when debugging
    3. Reading the .conf file is quicker
    4. Parsing the .conf file is simpler, as we can ignore the null case
    """
    keys_to_delete = ['mode']  # Unnecessary at this point - we were in CONFIG mode
    for (option, value) in json_rep.items():
        if value is None or value is False:
            keys_to_delete.append(option)
    for key in keys_to_delete:
        del json_rep[key]

    last_conf_dir = Path(".last_confs").resolve()
    safe_create_dir(last_conf_dir)
    out_file_name = f"last_conf_{datetime.now().strftime('%d_%m_%Y__%H_%M_%S')}.conf"
    out_file_path = last_conf_dir / out_file_name
    run_logger.debug(f"Saving last configuration file to {out_file_path}")
    with out_file_path.open("w+") as out_file:
        json.dump(json_rep, out_file, indent=4, sort_keys=True)

    return json_rep


def read_from_conf_file(args: argparse.Namespace) -> None:
    """
    Reads data from the configuration file given in the command line and adds each key to the args namespace if the key
    is undefined there. For more details, see the invoked method read_from_conf.
    @param args: A namespace containing options from the command line, if any (args.files[0] should always be a .conf
        file when we call this method)
    """
    assert args.mode == Mode.CONF, "read_from_conf_file() should only be invoked in CONF mode"

    conf_file_name = Path(args.files[0])
    assert conf_file_name.suffix == ".conf", f"conf file must be of type .conf, instead got {conf_file_name}"

    with conf_file_name.open() as conf_file:
        configuration = json.load(conf_file)
        read_from_conf(configuration, args)


# features: read from conf. write last to last_conf and to conf_date.
def read_from_conf(configuration: Dict[str, Any], args: argparse.Namespace) -> None:
    """
    Reads data from the input dictionary [configuration] and adds each key to the args namespace if the key is
    undefined there.
    Note: a command line definition trumps the definition in the file.
    If in the .conf file solc is 4.25 and in the command line --solc solc6.10 was given, sol6.10 will be used
    @param configuration: A json object in the conf file format
    @param args: A namespace containing options from the command line, if any
    """

    for option in configuration:
        if hasattr(args, option):
            val = getattr(args, option)
            if val is None or val is False:
                setattr(args, option, configuration[option])

    assert 'files' in configuration, "configuration file corrupted: key 'files' must exist at configuration"
    args.files = configuration['files']  # Override the current .conf file
