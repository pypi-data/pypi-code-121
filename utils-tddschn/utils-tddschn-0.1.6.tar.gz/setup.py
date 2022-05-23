# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['utils_tddschn']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'utils-tddschn',
    'version': '0.1.6',
    'description': '',
    'long_description': '',
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/utils-tddschn',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
