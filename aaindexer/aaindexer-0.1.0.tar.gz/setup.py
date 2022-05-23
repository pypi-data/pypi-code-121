# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aaindexer']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0.0,<8.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pyparsing>=3.0.8,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=12.4.1,<13.0.0']

entry_points = \
{'console_scripts': ['aaindexer = aaindexer.cli:main']}

setup_kwargs = {
    'name': 'aaindexer',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Michael Milton',
    'author_email': 'michael.r.milton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
