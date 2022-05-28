import os
import functools
import subprocess
from collections import abc

import numpy as np
import torch


def is_array_or_tensor(x):
    return isinstance(x, np.ndarray) or isinstance(x, torch.Tensor)


def is_seq_of(seq, expected_type, seq_type=None):
    """Check whether it is a sequence of some type.

    Args:
        seq (Sequence): The sequence to be checked.
        expected_type (type): Expected type of sequence items.
        seq_type (type, optional): Expected sequence type.

    Returns:
        bool: Whether the obj is the seq of the expected type.
    """
    if not isinstance(expected_type, type):
        raise TypeError(f"Expected type should be type, but got {type(expected_type)}")
    if seq_type is None:
        exp_seq_type = abc.Sequence
    else:
        if not isinstance(seq_type, type):
            raise TypeError(f"Seqence type should be type, but got {type(seq_type)}")
        exp_seq_type = seq_type
    if not isinstance(seq, exp_seq_type):
        return False
    for item in seq:
        if not isinstance(item, expected_type):
            return False
    return True


def is_list_of(seq, expected_type):
    """Check whether it is a list of some type."""
    return is_seq_of(seq, expected_type, seq_type=list)


def is_tuple_of(seq, expected_type):
    """Check whether it is a tuple of some type."""
    return is_seq_of(seq, expected_type, seq_type=tuple)


def check_prerequisites(
    prerequisites,
    checker,
    msg_tmpl='Prerequisites "{}" are required in method "{}" but not ' "found, please install them first.",
):
    """A decorator to check if prerequisites are satisfied.

    Args:
        prerequisites (str of list[str]): Prerequisites to be checked.
        checker (function): The checker method that returns True if a
            prerequisite is meet, False otherwise.
        msg_tmpl (str): The message template with two variables.

    Returns:
        decorator: A specific decorator.
    """

    def wrap(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            requirements = [prerequisites] if isinstance(prerequisites, str) else prerequisites
            missing = []
            for item in requirements:
                if not checker(item):
                    missing.append(item)
            if missing:
                print(msg_tmpl.format(", ".join(missing), func.__name__))
                raise RuntimeError("Prerequisites not meet.")
            else:
                return func(*args, **kwargs)

        return wrapped_func

    return wrap


def _check_executable(cmd):
    if subprocess.call(f"which {cmd}", shell=True) != 0:
        return False
    else:
        return True


def requires_executable(prerequisites):
    """A decorator to check if some executable files are installed.

    Example:
        >>> @requires_executable('ffmpeg')
        >>> def func(x):
        >>>     return x
    """
    return check_prerequisites(prerequisites, checker=_check_executable)


def update_path(path, variable_name="PATH"):
    """
    Update envrionment variable path.

    Args:
        path (str): new path to be inserted
        variable_name: path variable name, e.g. PATH, PYTHONPATH. (default PATH)
    """
    env_copy = os.environ.copy()
    env_copy[variable_name] = path + ":" + env_copy[variable_name]
    os.environ.update(env_copy)
