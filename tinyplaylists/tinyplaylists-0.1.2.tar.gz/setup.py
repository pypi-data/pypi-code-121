# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tinyplaylists']

package_data = \
{'': ['*']}

install_requires = \
['music-tag>=0.4.3,<0.5.0']

setup_kwargs = {
    'name': 'tinyplaylists',
    'version': '0.1.2',
    'description': 'A tiny library to organize audio files',
    'long_description': None,
    'author': 'platers',
    'author_email': 'platers81@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
