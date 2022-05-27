# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['habitat_tools']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.20.0,<0.21.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'habitat-tools',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Warren Snowden',
    'author_email': 'warren.snowden@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
