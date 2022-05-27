#!/usr/bin/env python3

"""
Create a saved_attributes_new.h5 template using a yaml configuration file (e.g.
saved_attributes_config.yml) and optionally existing records (saved_attributes.h5).

If the yaml config file is not provided, it will dump the existing model to a file
existing_config.yml. If both files are provided, it will update the model based on the
yaml config and keep corresponding records from the h5 file. Records from groups/motors
absent from the yaml config will be discarded.

E.g.:
`python path_to/update_saved_attributes.py --conf saved_attributes_config.yml --file saved_attributes.h5`
"""
import argparse
import copy

from h5py import File
import oyaml as yaml
from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Optional


def generate_config(
    yaml_config: Optional[Dict[str, Dict[str, str]]],
    h5_config: Optional[Dict[str, List[Dict[str, Any]]]],
) -> Optional[Dict[str, Any]]:
    """
    Generate saved attributes based on the new config and existing records.

    It uses the keys from the new config for the output model; records related to keys
    absent from the new config are discarded. For already existing groups, None records
    will be created for the new keys.

    :param yaml_config: the new config
    :param h5_config: a config extracted from an existing saved_attributes.h5 file
    :return: the updated config
    """
    final_config = {}
    if yaml_config is None:
        return h5_config
    if h5_config is None:
        return yaml_config

    h5_subgroups = list(h5_config.keys())
    if len(h5_subgroups) == 0:
        raise ValueError("No model defined in h5_config")

    # get the number of existing records per group
    group_records: Dict[str, int] = {}  # e.g. {'/Default': 1}
    for subgroup in h5_subgroups:
        group = "/" + subgroup.split(sep="/", maxsplit=2)[1]
        if not group_records.get(group):
            group_records[group] = len(h5_config[subgroup]) - 1
            # index 0 is the metadata
    print(f"Number of existing records: {group_records}")
    print("Using subgroups of the config file and adding records from the h5 file.")

    # check if config file subgroups exist in the h5 file
    for yaml_subgroup, inner_value in yaml_config.items():
        # example of yaml_subgroup:  '/Default/Sample'
        group_name = "/" + yaml_subgroup.split(sep="/", maxsplit=2)[1]
        value: List[Dict[str, str]] = [inner_value]

        if h5_config.get(yaml_subgroup, None):
            # h5_config[yaml_subgroup] is a list of dictionaries (records)
            h5_subgroup_keys = list(h5_config[yaml_subgroup][0].keys())
            for idx in range(1, group_records[group_name] + 1):
                record: Dict[str, str] = {}
                for key in inner_value:
                    if key in h5_subgroup_keys:
                        # h5_config[yaml_subgroup][idx] is a dict (a record)
                        record[key] = h5_config[yaml_subgroup][idx][key]
                    else:
                        record[key] = "None"
                value.append(record)
        else:
            # -> for a new motor, None values have to be set for the number of records
            # -> for a brand-new group, nothing to add
            if group_records.get(group_name, None):  # new motor for an existing group
                for idx in range(group_records[group_name]):
                    record = {}
                    for key in inner_value:
                        record[key] = "#fff" if key == "Color" else "None"
                    value.append(record)

        final_config[yaml_subgroup] = value

    return final_config


def generate_saved_attributes(path: Path, groups: Optional[Dict[str, Any]]) -> bool:
    """
    Add new group into saved attributes file.

    Example of groups:
    {"/Default/Sample": {
        "X ['Position'][mm]",
        "Y ['Position'][mm]",
        "Yaw ['Position'][deg]"
        }
    }
    Note that Attribute name has to be in single parentheses.
    Example of nested attribute can be "X ['Motor group', 'Position']"

    :param path: path to the saved attribute file
    :param groups: dict containing group : header pairs
    :return: True if everything went fine
    """
    if groups is None:
        print("No config defined, type 'python update_saved_attributes.py --help'")
        return False
    for group, data in groups.items():
        if isinstance(data, list):
            # it means that data contains records; the model is at index 0
            df = pd.DataFrame(data, columns=list(data[0].keys()))
        else:
            # data is just the model, no records
            df = pd.DataFrame(data, columns=list(data.keys()), index=[0])
        df.to_hdf(path, group, format="table")
    return True


def get_yaml_config(filename: Path) -> Dict[str, Dict[str, str]]:
    """Open and load a yaml configuration file for the saved attributes."""
    with filename.open(mode="r", encoding="utf-8") as config_file:
        new_conf = yaml.load(config_file, Loader=yaml.SafeLoader)
    return check_config(new_conf)


def check_config(config: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Format the new config.

    :param config: the config loaded from the yaml configuration file.
    """
    result: Dict[str, Any] = {}
    groups = config.get("groups", ["/Default"])
    motors = config.get("motors", None)

    if motors is None:
        raise ValueError("mandatory key 'motors' absent, invalid config")

    for group in groups:
        new_group = group if group.startswith("/") else "/" + group
        for motor, attributes in motors.items():
            new_motor = motor if motor.startswith("/") else "/" + motor
            result[new_group + new_motor] = {
                "Color": "None",
                "Time": "None",
                "Comment": "None",
            }
            for attribute in attributes:
                result[new_group + new_motor][attribute] = "None"
    return result


def get_existing_config(filename: Path) -> Dict[str, Any]:
    """
    Extract config and records from an existing h5 file.

    :param filename: path to the saved_attributes.h5 file
    """
    config: Dict[str, Any] = {}
    with File(filename, "r") as h5file:
        for group in h5file:
            for subgroup in h5file[group]:
                key = "/".join(["", group, subgroup])
                df = pd.read_hdf(filename, key=key)
                config[key] = df.reset_index().to_dict(orient="records")
    return config


def save_existing_model(config: Dict[str, Any], path: Path) -> None:
    """
    Save a config after dropping all records.

    :param config: dict, config containing the model at index 0 and then records
    :param path: Path, where to save the extracted model
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    groups: List[str] = []
    motors: Dict[str, List[str]] = {}

    for key in config:
        try:
            group, motor = key.split("/", maxsplit=2)[1:]
            # expected ["", "group_name", "motor_name"]
        except ValueError:
            raise ValueError(f"Invalid key '{key}', expecting '/group_name/motor_name'")
        if group not in groups:
            groups.append(group)
        if motor not in motors:
            motors[motor] = list(copy.deepcopy(config[key][0]).keys())
            for item in ["index", "Color", "Time", "Comment"]:
                motors[motor].remove(item)

    with path.open(mode="w", encoding="utf-8") as file:
        yaml.dump({"groups": groups, "motors": motors}, stream=file)


if __name__ == "__main__":
    # Parse arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf",
        help="Path of a yml configuration file",
        default=None,
    )
    parser.add_argument(
        "--file",
        help="Path of an existing 'saved_attributes.h5' file",
        default=None,
    )

    parser.add_argument(
        "--dir",
        help="Directory where to save the new file",
        default=None,
    )
    args = parser.parse_args()

    new_config = (
        get_yaml_config(filename=Path(args.conf)) if args.conf is not None else None
    )

    existing_config = (
        get_existing_config(filename=Path(args.file)) if args.file is not None else None
    )

    if args.dir is not None:
        savedir = Path(args.dir)
    elif existing_config is not None:
        savedir = Path(args.file).parent
    elif new_config is not None:
        savedir = Path(args.conf).parent
    else:
        raise ValueError("No saving directory defined")

    if existing_config is not None:
        save_existing_model(existing_config, path=savedir / "existing_config.yml")

    output_config = generate_config(
        yaml_config=new_config,
        h5_config=existing_config,
    )

    generate_saved_attributes(
        path=savedir / "saved_attributes_updated.h5",
        groups=output_config,
    )
