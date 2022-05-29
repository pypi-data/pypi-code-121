# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mongos']

package_data = \
{'': ['*']}

install_requires = \
['motor>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'pbt-mongo',
    'version': '1.0.0',
    'description': 'Mongo driver',
    'long_description': None,
    'author': 'everhide',
    'author_email': 'i.tolkachnikov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
