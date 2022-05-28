# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src', 'src.ml', 'src.ml.model', 'src.ml.sdk', 'src.ml.sdk.watchmen']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.2,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'watchmen-ml-python-sdk',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'luke0623',
    'author_email': 'luke0623@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
