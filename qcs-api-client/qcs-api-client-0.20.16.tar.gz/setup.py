# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qcs_api_client',
 'qcs_api_client.api',
 'qcs_api_client.api.account',
 'qcs_api_client.api.authentication',
 'qcs_api_client.api.client_applications',
 'qcs_api_client.api.default',
 'qcs_api_client.api.endpoints',
 'qcs_api_client.api.engagements',
 'qcs_api_client.api.quantum_processors',
 'qcs_api_client.api.reservations',
 'qcs_api_client.api.translation',
 'qcs_api_client.client',
 'qcs_api_client.client._configuration',
 'qcs_api_client.models',
 'qcs_api_client.operations',
 'qcs_api_client.operations.asyncio',
 'qcs_api_client.operations.asyncio_from_dict',
 'qcs_api_client.operations.sync',
 'qcs_api_client.operations.sync_from_dict',
 'qcs_api_client.util']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.1.0,<21.0.0',
 'httpx>=0.15.0,<0.16.0',
 'iso8601>=0.1.13,<0.2.0',
 'pydantic>=1.7.2,<2.0.0',
 'pyjwt>=1.7.1,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'retrying>=1.3.3,<2.0.0',
 'rfc3339>=6.2,<7.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'qcs-api-client',
    'version': '0.20.16',
    'description': 'A client library for accessing the Rigetti QCS API',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/qcs-api-client-python/badge/?version=latest)](https://qcs-api-client-python.readthedocs.io/en/latest/?badge=latest)\n\n# QCS API Client\n\nA client library for accessing the [Rigetti QCS API](https://docs.api.qcs.rigetti.com/).\n\n## Usage\n\n### Synchronous Usage\n\n```python\nfrom qcs_api_client.client import build_sync_client\nfrom qcs_api_client.models import ListReservationsResponse\nfrom qcs_api_client.operations.sync import list_reservations\n\nwith build_sync_client() as client:\n    response: ListReservationsResponse = list_reservations(client=client).parsed\n```\n\n### Asynchronous Usage\n\n```python\nfrom qcs_api_client.client import build_async_client\nfrom qcs_api_client.models import ListReservationsResponse\nfrom qcs_api_client.operations.asyncio import list_reservations\n\n# Within an event loop:\nasync with build_async_client() as client:\n    response: ListReservationsResponse = await list_reservations(client=client).parsed\n```\n\n### Configuration\n\nBy default, initializing your client with `build_sync_client` or `build_async_client` will\nuse `QCSClientConfiguation.load` to load default configuration values. This function accepts:\n\n- A profile name (env: `QCS_PROFILE_NAME`). The name of the profile referenced in your settings\n  file. If not provided, `QCSClientConfiguation.load` will evaluate this to a `default_profile_name`\n  set in your settings file or "default".\n- A settings file path (env: `QCS_SETTINGS_FILE_PATH`). A path to the current user\'s settings file in TOML format. If not provided,  `QCSClientConfiguation.load` will evaluate this to `~/.qcs/settings.toml`.\n- A secrets file path (env: `QCS_SECRETS_FILE_PATH`). A path to the current user\'s secrets file in TOML format. If not provided,  `QCSClientConfiguation.load` will evaluate this to `~/.qcs/secrets.toml`. The user should have write access to this file, as the client will attempt to update the file with refreshed access tokens as necessary.\n     \nIf you need to specify a custom profile name or path you can initialize your client accordingly:\n\n```python\nfrom qcs_api_client.client import build_sync_client, QCSClientConfiguration\nfrom qcs_api_client.models import ListReservationsResponse\nfrom qcs_api_client.operations.sync import list_reservations\n\nconfiguration = QCSClientConfiguration.load(\n    profile_name=\'custom\',\n    secrets_file_path=\'./path/to/custom/secrets.toml\',\n    settings_file_path=\'./path/to/custom/settings.toml\',\n)\n\nwith build_sync_client(configuration=configuration) as client:\n    response: ListReservationsResponse = list_reservations(client=client).parsed\n```\n\n## Development\n\nThe source code for this repository is synchronized from another source. No commits made directly to GitHub will be retained.\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rigetti/qcs-api-client-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
