# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clearview']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'clearview',
    'version': '0.1.0',
    'description': 'SDK for Clearview AI',
    'long_description': 'Please see the documentation at https://docs.clearview.ai.',
    'author': 'Clearview AI',
    'author_email': 'info@clearview.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://clearview.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
