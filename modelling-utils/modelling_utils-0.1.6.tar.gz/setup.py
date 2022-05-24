# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modelling_utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'cycler>=0.11.0,<0.12.0',
 'loguru>=0.6.0,<0.7.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.22.3,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'modelling-utils',
    'version': '0.1.6',
    'description': ' Utility functions and data structure for aiding in Analog Integrated Circuit Modelling using Python',
    'long_description': None,
    'author': 'Diogo André',
    'author_email': 'das.dias6@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/das-dias/modelling_utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
