# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aioinject', 'aioinject.ext']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aioinject',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Doctor',
    'author_email': 'thirvondukr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
