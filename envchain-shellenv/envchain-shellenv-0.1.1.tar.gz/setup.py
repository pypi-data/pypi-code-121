# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['envchain_shellenv']

package_data = \
{'': ['*'], 'envchain_shellenv': ['examples/*']}

install_requires = \
['keyring[keyring]>=23.5.1,<24.0.0']

entry_points = \
{'console_scripts': ['eesh = envchain_shellenv.cli:main_sync',
                     'envchain-shellenv = envchain_shellenv.cli:main_sync']}

setup_kwargs = {
    'name': 'envchain-shellenv',
    'version': '0.1.1',
    'description': 'envchain shellenv - prints export statements for your secrets in the keychain',
    'long_description': '',
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/envchain-shellenv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
