# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neuralwatermark']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.11.0,<2.0.0']

setup_kwargs = {
    'name': 'neuralwatermark',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Doodle',
    'author_email': 'saurabh.pandey.2171993@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
