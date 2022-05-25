# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codingfd_foobar_20220520_1']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'codingfd-foobar-20220520.1',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'neokeeper',
    'author_email': 'fand@coding.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
