""" File handling """
import json


def read_json_from_file(filename: str, encoding: str = 'utf-8') -> dict:
    """Load json configuration file.
    :param filename:
        Path to file.
    :param encoding:
        Encoding in which the file is read.
    :return:
        Loaded configuration as a dict.
    """
    if not filename:
        raise ValueError('Filename must be provided.')

    config = None
    with open(filename, encoding=encoding) as file:
        config = json.load(file)
    return config


def write_json_to_file(dictionary: dict, filename: str, encoding: str = 'utf-8') -> None:
    """
    Write dictionary to file
    :param dictionary:
        dictionary to be stored.
    :param filename:
        path to config file.
    :param encoding:
        Encoding in which the file is read
    """
    if not filename:
        raise ValueError('Filename must be provided.')

    with open(filename, 'w', encoding=encoding) as outfile:
        json.dump(dictionary, outfile, indent=4)
