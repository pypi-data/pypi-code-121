import os

import pandas as pd


def convert_yml_to_hdf5(path_to_yml, path_to_hdf5):
    """
    Convert old YAML formatted save file into new HDF5 format.

    :param path_to_yml: Path to the input YAML file
    :type path_to_yml: str
    :param path_to_hdf5: Path to the output HDF5 file
    :type path_to_hdf5: str
    """
    with open(path_to_yml, "r") as input_file:
        input_attributes = yaml.load(input_file, Loader=yaml.Loader)

    groups = input_attributes["Preset groups"]
    subgroup_units = {}
    for group, subgroups in groups.items():
        for subgroup, values in subgroups.items():
            group_path = os.path.join(group, subgroup)
            columns = values["columns"]
            rows = values["rows"]

            new_columns = {"Color": ["None"], "Time": ["None"], "Comment": ["None"]}
            for device_id, attribute in columns[1:]:
                device_attribute = f"{device_id}{attribute[:-1]}"
                if device_attribute not in subgroup_units:
                    unit = input(f"Set unit for {device_attribute} (mm): ")
                    if unit == "":
                        unit = "mm"
                    subgroup_units[device_attribute] = unit
                new_columns[
                    f"{device_id} {attribute[:-1]}[{subgroup_units[device_attribute]}]"
                ] = ["None"]
            for row in rows:
                for column_index, column_id in enumerate(new_columns.keys()):
                    row_value = row[column_index]
                    if column_index > 2 and row_value not in (None, "None", ""):
                        try:
                            row_value, _ = row_value.split(" ")
                        except ValueError:
                            print(repr(row_value))
                    new_columns[column_id].append(str(row_value))

            df = pd.DataFrame(new_columns, columns=list(new_columns.keys()))
            # Save group into HDF5 file.
            # Use format table and compression level 1
            # I was testing all compression levels without much gain of size.
            # Level 1 however gives almost 30% size decrease
            df.to_hdf(path_to_hdf5, group_path, format="table", complevel=1)


def generate_saved_attributes(path, groups):
    """
    Add new group into saved attributes file.

    Example of groups:
    {"/Default/Sample": {"X ['Position'][mm]", "Y ['Position'][mm]", "Yaw ['Position'][deg]"}}
    Note that Attribute name has to be in single parentheses.
    Example of nested attribute can be "X ['Motor group', 'Position']"

    :param path: path to the saved attribute file
    :param groups: dict containing group : header pairs
    """
    for group, data in groups.items():
        df = pd.DataFrame(data, columns=list(data.keys()))
        df.to_hdf(path, group, format="table")


if __name__ == "__main__":
    import argparse

    import oyaml as yaml

    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        help="Input path for saved attributes",
        default="./saved_attributes.att",
    )
    parser.add_argument(
        "--output",
        help="Path where to save new modified file",
        default="./saved_attributes_mod.att",
    )
    parser.add_argument("--chdir", help="Path to active directory", default="./")
    args = parser.parse_args()

    # Set active directory
    os.chdir(args.chdir)

    generate_saved_attributes(
        "/usr/local/share/pycharm-projects/bt_p07_sept_2021/bt_p07_sept_2021/saved_attributes.h5",
        {
            "/Default/Phase Plate": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "PP-X ['Position'][mm]": ["None"],
                "PP-Y ['Position'][mm]": ["None"],
                "PP-Z ['Position'][mm]": ["None"],
                "PP-Roll ['Position'][deg]": ["None"],
                "PP-Pitch ['Position'][deg]": ["None"],
                "PP-Yaw ['Position'][deg]": ["None"],
            },
            "/Default/MLL Down": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "MLL-DOWN-X ['Position'][mm]": ["None"],
                "MLL-DOWN-Y ['Position'][mm]": ["None"],
                "MLL-DOWN-Z ['Position'][mm]": ["None"],
                "MLL-DOWN-Roll ['Position'][deg]": ["None"],
                "MLL-DOWN-Pitch ['Position'][deg]": ["None"],
                "MLL-DOWN-Yaw ['Position'][deg]": ["None"],
            },
            "/Default/MLL Up": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "MLL-UP-X ['Position'][mm]": ["None"],
                "MLL-UP-Y ['Position'][mm]": ["None"],
                "MLL-UP-Z ['Position'][mm]": ["None"],
                "MLL-UP-Roll ['Position'][deg]": ["None"],
                "MLL-UP-Pitch ['Position'][deg]": ["None"],
                "MLL-UP-Yaw ['Position'][deg]": ["None"],
            },
            "/Default/Order sorting": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "OSB-X ['Position'][mm]": ["None"],
                "OSB-Y ['Position'][mm]": ["None"],
                "OSB-Z ['Position'][mm]": ["None"],
            },
            "/Default/Aperture": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "APT-X ['Position'][mm]": ["None"],
                "APT-Y ['Position'][mm]": ["None"],
                "APT-Z ['Position'][mm]": ["None"],
                "APT-Pitch ['Position'][deg]": ["None"],
                "APT-Yaw ['Position'][deg]": ["None"],
            },
            "/Default/Sample": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "SAM-X ['Position'][mm]": ["None"],
                "SAM-Y ['Position'][mm]": ["None"],
                "SAM-Z ['Position'][mm]": ["None"],
                "SCAN-X ['Position'][um]": ["None"],
                "SCAN-Y ['Position'][um]": ["None"],
                "SCAN-Z ['Position'][um]": ["None"],
            },
            "/Default/Microscope": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "MIC-X ['Position'][mm]": ["None"],
                "MIC-Y ['Position'][mm]": ["None"],
                "MIC-Z ['Position'][mm]": ["None"],
            },
            "/Default/Beamstop": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "BS-X ['Position'][mm]": ["None"],
                "BS-Y ['Position'][mm]": ["None"],
            },
            "/Default/Lambda-Compton": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "COMPT-DET-X ['Position'][mm]": ["None"],
                "COMPT-DET-Z ['Position'][mm]": ["None"],
            },
            "/Default/Lambda-Far": {
                "Color": ["None"],
                "Time": ["None"],
                "Comment": ["None"],
                "LambdaFar-X ['Position'][mm]": ["None"],
                "LambdaFar-Y ['Position'][mm]": ["None"],
                "LambdaFar-Z ['Position'][mm]": ["None"],
            },
        },
    )
    # convert_yml_to_hdf5(args.input, args.output)
