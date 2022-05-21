# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['async_tg_bot']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'async-tg-bot',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'levch',
    'author_email': 'levchenko.d.a1998@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
