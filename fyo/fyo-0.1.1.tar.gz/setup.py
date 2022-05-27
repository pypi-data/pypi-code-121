# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fyo']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fyo',
    'version': '0.1.1',
    'description': 'Pure syntactic sugar for filesystem tasks.',
    'long_description': "# Yoyo - pure synthatic sugar for filesystem tasks\n\n**Yoyo** extends python's built-in `pathlib` module with a few syntactic sugar methods.\n\nThis package is a work in progress.\n",
    'author': 'ericmiguel',
    'author_email': 'ericmiguel@id.uff.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ericmiguel/fyo',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
