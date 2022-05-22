# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ready_logger']

package_data = \
{'': ['*']}

install_requires = \
['psutil>=5.9.1,<6.0.0']

setup_kwargs = {
    'name': 'ready-logger',
    'version': '0.1.4',
    'description': 'Easily configure loggers.',
    'long_description': None,
    'author': 'Dan Kelleher',
    'author_email': 'dan@danklabs.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
