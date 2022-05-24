# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['importnow']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'importnow',
    'version': '0.1.1',
    'description': 'import for chads https://github.com/msaroufim/importnow',
    'long_description': None,
    'author': 'Mark Saroufim',
    'author_email': 'marksaroufim@fb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
