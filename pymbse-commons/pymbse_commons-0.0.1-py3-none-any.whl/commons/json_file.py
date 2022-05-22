import json


def read(json_file_path: str) -> dict:
    """Function reading a json file and returning a list of
    dictionaries with block definitions.

    :param json_file_path: a path to a json file
    :return: a list of dictionaries with geometry definition (block definition)
    """
    with open(json_file_path) as f:
        return json.load(f)


def write(file_path: str, content: dict) -> None:
    with open(file_path, "w") as file:
        json.dump(content, file)
