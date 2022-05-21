"""Module with functions for 'types' subpackage."""

from __future__ import annotations
from typing import Callable, Any, Union, Iterable
import ast


def str_to_infer_type(string_var: str) -> Any:
    """Convert string to another type (for example to int, float, list or dict).

    Args:
        string_var (str): String that should be converted.

    Returns:
        Any: New inferred type.

    Examples:
        >>> type(str_to_infer_type("1"))
        <class 'int'>
        >>> type(str_to_infer_type("1.2"))
        <class 'float'>
        >>> type(str_to_infer_type("['one']"))
        <class 'list'>
        >>> type(str_to_infer_type("{'one': 1}"))
        <class 'dict'>
    """
    return ast.literal_eval(string_var)


def json_to_py(json: dict, replace_comma_decimal: bool = True, replace_true_false: bool = True) -> Any:
    """Take json and eval it from strings. If string to string, if float to float, if object then to dict.

    When to use? - If sending object as parameter in function.

    Args:
        json (dict): JSON with various formats as string.
        replace_comma_decimal (bool, optional): Some countries use comma as decimal separator (e.g. 12,3).
            If True, comma replaced with dot (Only if there are no brackets (list, dict...)
            and if not converted to number string remain untouched) . For example '2,6' convert to 2.6.
            Defaults to True
        replace_true_false (bool, optional): If string is 'false' or 'true' (for example from javascript),
            it will be capitalized first for correct type conversion. Defaults to True

    Returns:
        dict: Python dictionary with correct types.

    Example:
        >>> # Can be beneficial for example when communicating with JavaScript
        >>> json_to_py({'one_two': '1,2'})
        {'one_two': 1.2}
    """
    import ast

    evaluated = json.copy()

    for i, j in json.items():

        replace_condition = isinstance(j, str) and "(" not in j and "[" not in j and "{" not in j

        if replace_comma_decimal and replace_condition:
            j = j.replace(",", ".")

        if replace_true_false and replace_condition:
            if j == "true":
                evaluated[i] = True
            if j == "false":
                evaluated[i] = False
            if j == "true" or j == "false":
                continue

        try:
            evaluated[i] = ast.literal_eval(j)
        except Exception:
            pass

    return evaluated


def str_to_bool(bool_str):
    """Convert string to bool. Usually used from argparse. Raise error if don't know what value.

    Possible values for True: 'yes', 'true', 't', 'y', '1'
    Possible values for False: 'no', 'false', 'f', 'n', '0'

    Args:
        bool_str (str):

    Raises:
        TypeError: If not one of bool values inferred, error is raised.

    Returns:
        bool: True or False

    Example:
        >>> str_to_bool("y")
        True

    Argparse example::

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--test",
            choices=(True, False),
            type=str_to_bool,
            nargs="?",
        )
    """
    if isinstance(bool_str, bool):
        return bool_str
    if bool_str.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif bool_str.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise TypeError("Boolean value expected.")
