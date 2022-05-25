import errno
import json
import os
import socket
import time
import uuid
from datetime import datetime

import jsonschema
import yaml

from vgscli.errors import SchemaValidationError, NoSuchFileOrDirectoryError


def expired(exp, delta=10):
    """
    :param exp: time in seconds since the Epoch.
    :param delta: time added to the current time to compensate request time
    :return: whether current time plus delta goes after exp time
    """
    return time.time() + delta > exp


def is_file_accessible(path, mode='r'):
    file_exists = os.path.exists(path) and os.path.isfile(path)
    if not file_exists:
        return False

    """
    Check if the file or directory at `path` can
    be accessed by the program using `mode` open flags.
    """
    try:
        f = open(path, mode)
        f.close()
    except IOError:
        return False
    return True


def is_port_accessible(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((host, port))
    except socket.error as e:
        return e.errno != errno.EADDRINUSE
    s.close()
    return True


def silent_file_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def to_timestamp(date):
    try:
        return int(datetime.timestamp(date))
    except (TypeError, ValueError):
        return None


def to_json(body):
    try:
        return json.loads(body.text)
    except Exception as ex:
        raise ex


# Initially there were dev/sandbox/live environments, but currently there is only dev and prod.
# So in order to stay backward compatible with sandbox/live we try to resolve everything that is not dev as prod
def resolve_env(env):
    if env == "dev":
        return env
    else:
        return "prod"


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

    Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    # noinspection PyBroadException
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except Exception:
        return False

    return str(uuid_obj) == uuid_to_test


def validate_yaml(file, schema_path, schema_root=os.path.dirname(__file__)):
    """
    Validates the file against the schema.

    Parameters
    ----------
    file: is the buffered content of the file
    schema_path: is the path relative to the working directory
    schema_root: was added to enable validating from different working directories like vgs-admin-cli-plugin
    """
    try:
        schema = read_file(schema_path, schema_root)
        file_content = yaml.full_load(file.read())

        jsonschema.validate(file_content, yaml.full_load(schema))

        return file_content
    except jsonschema.exceptions.ValidationError as e:
        raise SchemaValidationError(str(e))


def read_file(file_path, file_root=os.path.dirname(__file__)):
    full_path = os.path.join(file_root, file_path)
    try:
        with open(full_path, 'r') as f:
            schema = f.read()
            f.close()
            return schema
    except FileNotFoundError:
        raise NoSuchFileOrDirectoryError(full_path)
