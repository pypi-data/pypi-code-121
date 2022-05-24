# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['miniops']

package_data = \
{'': ['*']}

install_requires = \
['minio>=7.1.8,<8.0.0', 'pandas>=1.4.2,<2.0.0', 'psutil>=5.9.1,<6.0.0']

setup_kwargs = {
    'name': 'miniops',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Federico Falconieri',
    'author_email': 'federico.falconieri@tno.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
