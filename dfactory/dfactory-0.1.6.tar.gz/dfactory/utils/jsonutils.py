# -*- coding: utf-8 -*-

"""
json utils
"""
import json


def read_json(src: str):
    """
    read json file into dict
    :param src: filename
    :return: dict read from json file
    """
    with open(src, encoding="utf-8") as fin:
        return json.loads((fin.read()))
