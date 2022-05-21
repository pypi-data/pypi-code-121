# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['varutils', 'varutils.plugs']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4,<5', 'varname>=0.8,<0.9']

setup_kwargs = {
    'name': 'varutils',
    'version': '0.0.7',
    'description': 'My personal Python module containing various useful utilities.',
    'long_description': '# varutils\nMy personal Python module containing various useful utilities.\n',
    'author': 'Andrew Sonin',
    'author_email': 'sonin.cel@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewsonin/varutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
