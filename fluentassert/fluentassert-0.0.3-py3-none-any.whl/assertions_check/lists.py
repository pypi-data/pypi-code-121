import json
import re
from xml.etree import ElementTree

import yaml

from ..exceptions import CheckError


def is_list(check_obj):
    try:
        assert isinstance(check_obj._val, list)
        return check_obj
    except AssertionError as e:
        raise CheckError('{} is not a list'.format(check_obj._val)) from e


def is_not_list(check_obj):
    try:
        assert not isinstance(check_obj._val, list)
        return check_obj
    except AssertionError as e:
        raise CheckError('{} is a list'.format(check_obj._val)) from e


def is_in_list(check_obj, _char):
    check_obj.is_list()
    try:
        assert _char in check_obj._val
        return check_obj
    except AssertionError as e:
        raise CheckError('{} does not contain : {}'.format(
            check_obj._val, _char)) from e


def is_not_in_list(check_obj, _char):
    check_obj.is_list()
    try:
        assert _char not in check_obj._val
        return check_obj
    except AssertionError as e:
        raise CheckError('{} does contain : {}'.format(
            check_obj._val, _char)) from e
