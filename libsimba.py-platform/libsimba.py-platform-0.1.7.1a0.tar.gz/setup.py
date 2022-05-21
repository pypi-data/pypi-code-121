# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libsimba', 'libsimba.auth', 'libsimba.base', 'libsimba.templates']

package_data = \
{'': ['*']}

install_requires = \
['hdwallet>=2.1.1,<3.0.0',
 'httpx>=0.21.1,<0.22.0',
 'requests>=2.25.1,<3.0.0',
 'web3>=5.28.0,<6.0.0']

entry_points = \
{'console_scripts': ['test = libsimba.simba:Simba.test']}

setup_kwargs = {
    'name': 'libsimba.py-platform',
    'version': '0.1.7.1a0',
    'description': '',
    'long_description': None,
    'author': 'Adam Brinckman',
    'author_email': 'abrinckm@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
