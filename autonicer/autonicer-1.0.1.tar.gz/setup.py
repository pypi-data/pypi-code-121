# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autonicer']

package_data = \
{'': ['*']}

install_requires = \
['astropy>4.2.1',
 'astroquery>0.4.3',
 'numpy>1.20.3',
 'pandas>1.2.4',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['autonicer = autonicer:run']}

setup_kwargs = {
    'name': 'autonicer',
    'version': '1.0.1',
    'description': 'A program that retrieves NICER observational data sets and performs a default data reduction process on the NICER observational data',
    'long_description': None,
    'author': 'Tsar Bomba Nick',
    'author_email': 'njkuechel@protonmail.com',
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
