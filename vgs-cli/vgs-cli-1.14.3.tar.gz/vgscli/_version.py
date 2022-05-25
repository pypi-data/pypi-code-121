from typing import Optional

import click
import requests
from semver import VersionInfo

from vgscli.text import bold, green

__version__ = '1.14.3'


# noinspection PyBroadException
def get_latest_version(**kwargs) -> Optional[VersionInfo]:
    try:
        response_json = requests.get('https://pypi.org/pypi/vgs-cli/json', **kwargs).json()
        return VersionInfo.parse(response_json['info']['version'])
    except Exception:
        return None


def check_for_updates() -> None:
    latest_version = get_latest_version(timeout=2)

    if latest_version and latest_version > __version__:
        message = f'CLI update available from {bold(green(__version__))} to {bold(green(str(latest_version)))}.'
        click.echo(message, err=True)


def version():
    return __version__
