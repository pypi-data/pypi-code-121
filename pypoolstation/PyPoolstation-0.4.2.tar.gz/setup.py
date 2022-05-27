# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypoolstation']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'pypoolstation',
    'version': '0.4.2',
    'description': 'Python library to interact with the API of the Poolstation (https://poolstation.net) domotic platform for pool equipment',
    'long_description': None,
    'author': 'cibernox',
    'author_email': 'miguel.camba@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
