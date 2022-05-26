# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prompt_importer']

package_data = \
{'': ['*']}

install_requires = \
['beancount>=2.3.5,<3.0.0', 'blessed>=1.19.1,<2.0.0']

setup_kwargs = {
    'name': 'prompt-importer',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Harry Eldridge',
    'author_email': 'eldridgemharry@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
