# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_sdk']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.0.0,<3.0.0',
 'click>=7.0,<9.0',
 'pydantic>=1.7.0,<2.0.0',
 'requests>=2.25.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.7.4,<4.0.0'],
 'dataframe': ['pandas>=1.0,<2.0', 'geopandas>=0.8.0,<0.9.0'],
 'test': ['pandas>=1.0,<2.0', 'geopandas>=0.8.0,<0.9.0']}

entry_points = \
{'console_scripts': ['uf-data-sdk = unfolded.data_sdk.cli:main']}

setup_kwargs = {
    'name': 'unfolded.data-sdk',
    'version': '0.8.0',
    'description': "Module for working with Unfolded Studio's Data SDK",
    'long_description': "# `unfolded.data-sdk`\n\nPython package for interfacing with [Unfolded](https://unfolded.ai)'s Data SDK.\n\nFor more documentation, refer to the [documentation website](https://docs.unfolded.ai/data-sdk).\n",
    'author': 'Kyle Barron',
    'author_email': 'kyle@unfolded.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
