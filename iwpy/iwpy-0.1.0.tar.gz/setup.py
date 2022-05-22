# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iwpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'iwpy',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Noah Biederbeck',
    'author_email': 'noah.biederbeck@tu-dortmund.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
