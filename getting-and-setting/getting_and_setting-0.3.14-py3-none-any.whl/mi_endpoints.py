import configparser
import keyring
import pathlib
from typing import Dict, List, Union
from functools import cache

from . mi_models import Endpoint


PATH = str(pathlib.Path.joinpath(pathlib.Path.home(), '.getting-and-setting.ini').absolute())
SERVICE_ID = 'getting-and-setting'


def mi_endpoint_save(endpoint: Endpoint) -> Endpoint:
    config = configparser.ConfigParser()
    config.read(PATH)

    config[f'endpoint.{endpoint.name}'] = {
        'host': endpoint.host,
        'port': endpoint.port,
        'usr': endpoint.usr
    }

    with open(PATH, 'w') as f:
        config.write(f)

    keyring.set_password(SERVICE_ID, endpoint.name, endpoint.pwd)

    return mi_endpoint_get(endpoint.name)

@cache
def mi_endpoint_get(name: str) -> Endpoint:
    config = configparser.ConfigParser()
    config.read(PATH)

    try:
        endpoint = dict(config[f'endpoint.{name}'])

    except KeyError:
        raise ValueError(f'Endpoint {name} not found in configuration')

    endpoint['pwd'] = keyring.get_password(SERVICE_ID, name)

    return Endpoint(name=name, **endpoint)


def mi_endpoint_delete(name: str) -> None:
    config = configparser.ConfigParser()
    config.read(PATH)

    config.remove_section(f'endpoint.{name}')

    with open(PATH, 'w') as f:
        config.write(f)

    try:
        keyring.delete_password(SERVICE_ID, name)

    except keyring.core.backend.errors.PasswordDeleteError:
        pass


def mi_endpoint_list() -> List[Endpoint]:
    config = configparser.ConfigParser()
    config.read(PATH)

    return [
        Endpoint(
            name = config[section].name.split('.')[1],
            host = config[section]['host'],
            port = config[section]['port'],
            usr = config[section]['usr'],
            pwd = keyring.get_password(
                SERVICE_ID,
                config[section].name.split('.')[1]
            )
        )
        for section
        in config.sections()
        if section.startswith('endpoint')
    ]