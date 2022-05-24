# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jamf']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'keyring>=23.5.1,<24.0.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'jamf',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Trenten Oliver',
    'author_email': 'trentenoliver@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
