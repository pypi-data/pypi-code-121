# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from io import open
import ast


def get_ast_parsed_code(path):
    """
    Open the path, retrieve text, and parse the
    text to create an ast tree of the code

    :param path: path to file location
    :return: ast representation of code in path.
    """
    with open(path, encoding="utf-8") as path_file:
        text = path_file.read()

    if isinstance(text, str):
        code_text = text.encode("utf-8", "ignore")
    else:
        code_text = str(text)

    parsed = ast.parse(code_text)

    return parsed
