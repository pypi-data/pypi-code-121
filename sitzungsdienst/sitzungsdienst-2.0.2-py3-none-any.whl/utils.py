from hashlib import md5
from typing import Any, List


def data2hash(data: Any) -> str:
    """
    Builds hash over given data

    :param data: typing.Any Data

    :return: str Hash
    """

    return md5(str(data).encode('utf-8')).hexdigest()


def flatten(data: List[list]) -> List[Any]:
    """
    Flattens list of lists

    :param data: list List of lists

    :return: list Flattened list
    """

    return [item for sublist in data for item in sublist]
