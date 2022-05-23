# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sentinel_django']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.4,<5.0.0']

setup_kwargs = {
    'name': 'sentinel-django',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Niranjan',
    'author_email': 'niranjannb7777@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
