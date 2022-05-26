# encoding: utf-8
from __future__ import absolute_import

import json
import random
import string
from functools import wraps

import requests
import six
from rapyuta_io.utils import APIError, ParameterMissingException, InvalidParameterException, \
    UnauthorizedError, ResourceNotFoundError, BadRequestError, InternalServerError, ConflictError, \
    ForbiddenError
from rapyuta_io.utils.settings import EMPTY, DEFAULT_RANDOM_VALUE_LENGTH
from six.moves import range

BEARER = "Bearer"


def prepend_bearer_to_auth_token(auth_token):
    if auth_token.startswith(BEARER):
        return auth_token
    else:
        return '{0} {1}'.format(BEARER, auth_token)


def create_auth_header(auth_token, project):
    return dict(Authorization=auth_token, project=project)


def get_error(response_data):
    try:
        err_response = json.loads(response_data)
        error_msg = err_response.get('error', None)
        if error_msg:
            return error_msg
        return err_response['response']['error']
    except (ValueError, TypeError, KeyError):
        return u''


def validate_key_value(obj):
    fields = ['id', 'key', 'value']
    for field in fields:
        field_value = obj.get(field, None)
        if field_value is None or field_value == '':
            raise ParameterMissingException(str.format("parameter {0} is missing", field))


def validate_list_of_strings(obj, parameter_name):
    if not isinstance(obj, list):
        raise InvalidParameterException('{0} must be a list'.format(parameter_name))
    for element in obj:
        if not isinstance(element, six.string_types):
            raise InvalidParameterException('Elements in {0} must be strings'.format(
                parameter_name))


def get_api_response_data(response, parse_full=False, errors=None, return_value=None):
    common_errors = {requests.codes.BAD_REQUEST: BadRequestError,
                     requests.codes.UNAUTHORIZED: UnauthorizedError,
                     requests.codes.NOT_FOUND: ResourceNotFoundError,
                     requests.codes.INTERNAL_SERVER_ERROR: InternalServerError,
                     requests.codes.CONFLICT: ConflictError,
                     requests.codes.FORBIDDEN: ForbiddenError}
    if errors:
        common_errors.update(errors)
    status_code = response.status_code
    if 200 <= status_code <= 299:
        if return_value:
            return return_value
        try:
            response_data = json.loads(response.text)
            if parse_full:
                return response_data
            else:
                return response_data['response']['data']
        except Exception as err:
            raise APIError(err)
    elif status_code in common_errors:
        raise common_errors[status_code](get_error(response.text))
    else:
        raise APIError(get_error(response.text))


def response_validator(parse_full=False, errors=None, return_value=None):
    def fun_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            return get_api_response_data(response, parse_full=parse_full,
                                         errors=errors, return_value=return_value)

        return wrapper

    return fun_wrapper


def write_to_file(file_name, content):
    file_ = open(file_name, 'w')
    file_.write(content)
    file_.close()
    return


def is_empty(obj):
    if obj is None or obj is EMPTY:
        return True
    return False


def remove_attributes(dict_obj, attr_list=list()):
    if dict_obj is not None:
        for attr in attr_list:
            dict_obj.pop(attr, None)
    return


def keep_attributes(dict_obj, attr_list=list()):
    for key in list(dict_obj):
        if key not in attr_list:
            dict_obj.pop(key, None)
    return


def generate_random_value(length=DEFAULT_RANDOM_VALUE_LENGTH):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def valid_list_elements(elements, type):
    if not isinstance(elements, list):
        return False
    return not [x for x in elements if not isinstance(x, type)]
