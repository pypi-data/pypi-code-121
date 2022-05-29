# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nextc', 'nextc.ast', 'nextc.compile', 'nextc.lexing', 'nextc.parse']

package_data = \
{'': ['*'], 'nextc': ['runtime/*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'llvmlite>=0.38.1,<0.39.0']

setup_kwargs = {
    'name': 'nextc',
    'version': '0.2',
    'description': 'The Next Programming Language for you.',
    'long_description': None,
    'author': 'VincentRPS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
