# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opta', 'opta.tools']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0']

setup_kwargs = {
    'name': 'opta',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'wol4aravio',
    'author_email': 'panovskiy.v@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
